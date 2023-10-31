"""
.. module:: tasking
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`Tasking` class which is the base class used
               to pattern interop with tasks across processes and machines.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>

"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []
__version__ = "1.0.0"
__maintainer__ = "Myron Walker"
__email__ = "myron.walker@gmail.com"
__status__ = "Development" # Prototype, Development or Production
__license__ = "MIT"


from typing import Dict, Optional, Tuple, Type

import multiprocessing
import multiprocessing.managers

import json
import logging
import os
import requests
import threading
import traceback

from pprint import pformat

from dataclasses import dataclass
from datetime import datetime
from logging.handlers import WatchedFileHandler

from uuid import uuid4

from mojo.errors.exceptions import NotOverloadedError, SemanticError

from mojo.results.model.progressinfo import ProgressInfo, ProgressType
from mojo.results.model.progresscode import ProgressCode

from mojo.xmods.xformatting import indent_lines
from mojo.xmods.ximport import import_by_name
from mojo.xmods.jsos import CHAR_RECORD_SEPERATOR

from mojo.interop.protocols.tasker.taskingresult import TaskingResult
from mojo.interop.protocols.tasker.taskeraspects import TaskerAspects, DEFAULT_TASKER_ASPECTS


def instantiate_tasking(module_name: str, tasking_name: str, task_id: str, parent_id: str, logdir: str, logfile: str,
                        log_level: int, notify_url: Optional[str], notify_headers: Optional[Dict[str, str]],
                        aspects: Optional[TaskerAspects] = DEFAULT_TASKER_ASPECTS):

    logger = None
    tasking = None

    module = import_by_name(module_name)

    if hasattr(module, tasking_name):

        log_handler = WatchedFileHandler(logfile)
        logging.basicConfig(format=logging.BASIC_FORMAT, level=log_level, handlers=[log_handler])

        logger = logging.getLogger("tasker-server")

        tasking_type: Type[Tasking] = getattr(module, tasking_name)

        tasking = tasking_type(task_id=task_id, parent_id=parent_id, logdir=logdir, logfile=logfile, logger=logger,
                               notify_url=notify_url, notify_headers=notify_headers, aspects=aspects)

    return tasking


class TaskingManager(multiprocessing.managers.SyncManager):
    """
        This is a process manager used for creating a :class:`TaskingManager`
        in a remote process that can be communicated with via a proxy.
    """

TaskingManager.register("instantiate_tasking", instantiate_tasking)


@dataclass
class StreamInfo:
    name: str
    type: str
    filename: str


@dataclass
class TaskingIdentity:
    module_name: str
    tasking_name: str

    def as_tuple(self) -> Tuple[str, str]:
        return self.module_name, self.tasking_name


class Tasking:
    """
    """

    def __init__(self, task_id: str, parent_id: str, logdir: str, logfile: str, logger: logging.Logger, 
                 notify_url: Optional[str] = None, notify_headers: Optional[dict] = None,
                 aspects: Optional[TaskerAspects] = DEFAULT_TASKER_ASPECTS):

        self._task_id = task_id
        if self._task_id is None:
            self._task_id = str(uuid4())

        self._parent_id = parent_id
        self._logdir = logdir
        self._logfile = logfile
        self._logger = logger
        self._notify_url = notify_url
        self._notify_headers = notify_headers
        self._aspects = aspects

        self._kwparams: dict = None

        self._task_status = ProgressCode.NotStarted
        self._task_thread = None

        self._running = False
        self._shutdown = False

        self._summary = {}
        self._summary_file = None
        self._summary_indent = 4

        self._metrics_streams = {}
        self._metrics_indent = None

        self._pause_gate = threading.Event()
        
        # The following variables are shared between process but must be updated in the parent process
        # when progress or state comes back from the child process
        self._result = None
        self._exception = None

        # The following variables are used by the task process state
        self._current_progress = None
        self._progress_queue: multiprocessing.JoinableQueue = None

        return

    @classmethod
    def get_identity(cls) -> TaskingIdentity:
        module_name = cls.__module__
        tasking_name = cls.__name__
        identity = TaskingIdentity(module_name=module_name, tasking_name=tasking_name)
        return identity

    @property
    def full_name(self):
        this_type = type(self)
        fname = f"{this_type.__module__}@{this_type.__name__}"
        return fname

    @property
    def result(self):
        return self._result

    @property
    def task_status(self):
        return self._task_status

    def add_metrics_stream(self, stream_name: str, stream_type: str):
        """
            Adds a new metrics stream
        """

        stream_filename = os.path.join(self._logdir, f"{stream_name}.jsos")

        stream_info = StreamInfo(stream_name, stream_type, stream_filename)
        self._metrics_streams[stream_name] = stream_info

        return

    def begin(self, kwparams: dict):
        """
            The `begin` method is called in order to stash the `kwparams` on the tasking instance
            and to create the result container.
        """
        self._kwparams = kwparams

        begin_msg = self.format_begin_message(kwparams)
        self._logger.info(begin_msg)

        return

    def cleanup(self):
        """
            Called to allow the tasking to cleanup any created resources.
        """
        return

    def execute(self, progress_queue: multiprocessing.JoinableQueue, kwparams: dict):
        """
            The `execute` method is called by the tasking service in order to trigger the execution
            of the task.
        """

        sgate = threading.Event()
        sgate.clear()

        ttargs = (sgate, progress_queue, kwparams)

        self._task_thread = threading.Thread(target=self._task_thread_entry, name="effect-dispatcher", args=ttargs, daemon=True)
        self._task_thread.start()

        sgate.wait()

        return

    def evaluate_results(self) -> int:
        """
            The `evaluate_results` method is called in order to process information to
            create a final status code for the given tasking.

            :returns: Returns the 'result_code' that is written into the tasking result.
        """
        return 0

    def finalize(self):
        """
            The `finalize` method is called in order to provide an opportunity for a tasking
            to finalize execution and cleanup resources as required.
        """
        finalize_msg = self.format_finalize_message()
        self._logger.info(finalize_msg)
        return
    
    def fire_perform(self):
        """
            The `fire_peform` allows for modification of the calling of the perform method.
        """
        return self.perform()

    def format_begin_message(self, kwparams: dict):
        """
            Formats the tasking 'BEGIN' log message.
        """
        
        begin_msg_lines = [
            f"------------------------------- TASKING BEGUN -------------------------------",
            f"  TASK_NAME: {self._result.task_name}",
            f"    TASK_ID: {self._result.task_id}",
            f"  PARENT_ID: {self._result.parent_id}",
            f"     LOGDIR: {self._logdir}",
            f"      START: {self._result.start}"
        ]

        kwparams_lines = pformat(kwparams, indent=4, width=200)
        kwparams_lines = indent_lines(kwparams_lines, level=1, indent=10)

        begin_msg_lines.append("  KWPARAMS:")
        begin_msg_lines.append(kwparams_lines)

        begin_msg = os.linesep.join(begin_msg_lines)

        return begin_msg

    def format_finalize_message(self):
        """
            Formats the tasking 'FINALIZE' log message.
        """

        finalize_msg_lines = [
            "------------------------------- TASKING FINALIZED -------------------------------"
            f"    TASK_NAME: {self._result.task_name}",
            f"      TASK_ID: {self._result.task_id}",
            f"    PARENT_ID: {self._result.parent_id}",
            f"       LOGDIR: {self._logdir}",
            f"        START: {self._result.start}",
            f"         STOP: {self._result.stop}",
            f"  RESULT_CODE: {self._result.result_code}",
        ]

        if self._result.exception is None:
            finalize_msg_lines.append(f"    EXCEPTION: None")
        else:
            finalize_msg_lines.append(f"    EXCEPTION: ")

            xcpt_lines = traceback.format_exception(self._result.exception)
            xcpt_lines = indent_lines(xcpt_lines, level=1, indent=10)
            finalize_msg_lines.append(xcpt_lines)

        finalize_msg = os.linesep.join(finalize_msg_lines)

        return finalize_msg
    
    def format_progress_message(self, progress: dict):
        """
            Formats a tasking 'PROGRESS' log message.
        """
        prog_msg_lines = ["PROGRESS"]

        progress_lines = pformat(progress, indent=4, width=200)
        progress_lines = indent_lines(progress_lines, level=1, indent=4)

        prog_msg_lines.append(progress_lines)

        prog_msg = os.linesep.join(prog_msg_lines)

        return prog_msg

    def initialize_metrics(self):
        """
            Called in order to initialize any metrics data contains needed by the tasking and also
            to initialize the full path to the summary file.
        """
        return

    def initialize_summary(self):
        """
            Called in order to initialize the Summary info dictionary that is used to write summary
            information to the summary file and also to initialize the full path to the summary file.
        """
        
        this_type = type(self)

        self._summary_file = os.path.join(self._logdir, "task-summary.json")
        self._summary = {
            "name": self.full_name,
            "type": this_type.__name__,
            "module": this_type.__module__,
            "id": self._result.task_id,
            "parent": self._result.parent_id,
            "start": self._result.start,
            "stop": None,
            "status": str(ProgressCode.Running.value),
            "metrics": self._metrics_streams,
            "result_code": None,
            "exception" : None
        }

        return

    def mark_errored(self):
        """
            Marks the tasking as having errored.  This indicates to the TaskingServer that shutdown of the
            tasking has begun.
        """
        self.mark_progress_errored()
        self._progress_queue.put_nowait(self._current_progress)
        return

    def mark_progress_complete(self):
        """
            The `mark_progress_complete` method is called to generate a :class:`ProgressInfo` completed.
        """
        self._task_status = ProgressCode.Completed
        self._current_progress.when = datetime.now()
        self._current_progress.status = ProgressCode.Completed
        return

    def mark_progress_errored(self):
        """
            The `mark_progress_errored` method is called to generate a :class:`ProgressInfo` errored.
        """
        self._task_status = ProgressCode.Errored
        self._current_progress.when = datetime.now()
        self._current_progress.status = ProgressCode.Errored
        return
    
    def mark_progress_paused(self):
        """
            The `mark_progress_paused` method is called to generate a :class:`ProgressInfo` paused.
        """
        self._task_status = ProgressCode.Paused
        self._current_progress.when = datetime.now()
        self._current_progress.status = ProgressCode.Paused
        return
    
    def mark_progress_running(self):
        """
            The `mark_progress_running` method is called to generate a :class:`ProgressInfo` running.
        """
        self._task_status = ProgressCode.Running
        self._current_progress.when = datetime.now()
        self._current_progress.status = ProgressCode.Running
        return

    def mark_progress_start(self):
        """
            The `mark_progress_start` method that is called to generate a :class:`ProgressInfo` running.
        """
        self._task_status = ProgressCode.Running
        self._current_progress = ProgressInfo(self._task_id, ProgressType.NumericRange, self.full_name,
                                              0, 0, 0, ProgressCode.Running, datetime.now(), {})
        return

    def notify_progress(self, progress: ProgressInfo):
        """
            The `notify_progress` method is called in order to send a progress notification to a
            progress notification concentrator.

            :param progress: The progress information to transmit.
        """

        if self._notify_url is not None:

            headers = {
                "Content-Type": "application/json"
            }
            if self._notify_headers is not None:
                headers.update(self._notify_headers)

            body = progress.as_dict()

            try:
                requests.post(self._notify_url, json=body, headers=headers)
            except Exception as xcpt:
                print(xcpt)
                self._logger.error(f"Failure during notification to url='{self._notify_url}'")

        return
    
    def pause(self):
        """
            Sends a Pause command to the remote tasking
        """

        self._task_status = ProgressCode.Paused
        self._pause_gate.clear()
        
        return
    
    def perform(self) -> bool:
        """
            The `perform` method is overloaded by derived tasking types in order to implement
            the performance of a unit of work.

            :returns: Returns a bool indicating if 'perform' should be called again in order
                      to complete more work.
        """
        errmsg = "Tasking.perform method must be overloaded in derived types."
        raise NotOverloadedError(errmsg)
    
    def resume(self):
        """
            Resumes the tasking loop
        """

        self._task_status = ProgressCode.Running
        self._pause_gate.set()
        
        return
    
    def shutdown(self):
        """
            Sends a Shutdown command to the remote tasking
        """

        self._running = False
        self._shutdown = True
        
        return

    def submit_progress(self):
        """
            Submits that the tasking as having made progress on some activity so the TaskingServer 'hang' detection
            does not trigger an inactivity timeout shutdown of the tasking.
        """

        self._current_progress.when = datetime.now()
        prog_dict = self._current_progress.as_dict()

        prog_msg = self.format_progress_message(prog_dict)
        self._logger.info(prog_msg)

        self._summary["progress"] = prog_dict
        self.write_summary()

        self._progress_queue.put_nowait(self._current_progress)
        
        self.notify_progress(self._current_progress)

        return

    def write_summary(self):
        """
            Writes an update of the tasking summary to the summary file.
        """
        
        with open(self._summary_file, 'w+') as sf:
            json.dump(self._summary, sf, indent=self._summary_indent, default=str)

        return
    
    def write_metrics(self, stream_name:str, metrics: dict):
        """
            Called in order to write a metrics payload to the taskings associated metrics stream file.
        """

        if stream_name in self._metrics_streams:

            stream_info: StreamInfo = self._metrics_streams[stream_name]

            with open(stream_info.filename, 'a+') as mf:
                json.dump(metrics, mf, indent=self._metrics_indent, default=str)
                mf.write(CHAR_RECORD_SEPERATOR)

        else:
            errmsg = "You must call `add_metrics_stream` to add a stream to the tasking before attempting to write to the stream."
            raise SemanticError(errmsg)

        return

    def _task_thread_entry(self, sgate: threading.Event, progress_queue: multiprocessing.JoinableQueue, kwparams: dict):

        # Update our local in process copy of these queues, because we have forked
        self._progress_queue = progress_queue

        self._result = TaskingResult(self.full_name, self._task_id, self._logdir, parent_id=self._parent_id)
        self._running = True

        self.initialize_summary()
        self.initialize_metrics()

        sgate.set()

        self.begin(kwparams)

        try:

            try:

                try:
                    self.mark_progress_start()
                    self.submit_progress()

                    while self._running:

                        if self._task_status == ProgressCode.Paused:
                            self.mark_progress_paused()
                            self.submit_progress()

                            self._pause_gate.wait()

                            if not self._running:
                                break

                            self.mark_progress_running()
                            self.submit_progress()

                        cont = self.fire_perform()
                        
                        self.submit_progress()

                        if not cont:
                            break
                    
                    if self._shutdown:
                        self.submit_progress()
                    else:
                        self.mark_progress_complete()

                    self.submit_progress()

                except Exception as innererr:
                    self._exception = innererr

                    self.mark_errored()

                finally:
                    self._result_code = self.evaluate_results()

            except Exception as evalerr:
                if self._result_code is None:
                    self._result_code = -999

                if self._exception is not None:
                    try:
                        raise evalerr from self._exception
                    except Exception as comberr:
                        self._exception = comberr
                else:
                    self._exception = evalerr

                self.mark_errored()

            # We still need to attempt to cleanup
            self.cleanup()

        except Exception as finalerr:
            if self._result_code is None:
                    self._result_code = -888

            if self._exception is not None:
                try:
                    raise finalerr from self._exception
                except Exception as comberr:
                    self._exception = comberr
            else:
                self._exception = finalerr

            self.mark_errored()

        finally:
            self._result.mark_result(self._result_code, self._exception)
            self._summary["stop"] = self._result.stop

            try:
                self.finalize()
            except Exception as xcpt:
                errmsg = traceback.format_exception(xcpt)
                self._logger.error(errmsg)

            self._running = False

            # Pushing the result to the progress queue indicates to the
            # monitoring thread or process that this tasking is complete
            # and shutting down.
            progress_queue.put(self._result)

        return
