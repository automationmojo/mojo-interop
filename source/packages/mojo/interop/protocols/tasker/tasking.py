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



from typing import Dict, Optional, Tuple, Type

import multiprocessing
import multiprocessing.managers

import json
import logging
import os
import requests
import threading
import traceback

from http import HTTPStatus
from pprint import pformat

from dataclasses import dataclass
from datetime import datetime
from logging import FileHandler

from uuid import uuid4

from mojo.errors.exceptions import NotOverloadedError, SemanticError
from mojo.errors.xtraceback import create_traceback_detail, format_traceback_detail

from mojo.results.model.resultcode import ResultCode
from mojo.results.model.resulttype import ResultType
from mojo.results.model.progressinfo import ProgressInfo, ProgressType
from mojo.results.model.progresscode import ProgressCode
from mojo.results.model.taskingresult import TaskingResult

from mojo.xmods.xdatetime import format_datetime_with_fractional
from mojo.xmods.xformatting import indent_lines_list
from mojo.xmods.ximport import import_by_name
from mojo.xmods.jsos import CHAR_RECORD_SEPERATOR

from mojo.interop.protocols.tasker.taskeraspects import TaskerAspects, DEFAULT_TASKER_ASPECTS
from mojo.interop.protocols.tasker.taskingevent import TaskingEvent


def instantiate_tasking(worker: str, wref: str, module_name: str, tasking_name: str, tasking_id: str, parent_id: str, output_dir: str,
                        logdir: str, logfile: str, log_level: int, events_endpoint: Tuple[str, int], notify_url: Optional[str], notify_headers: Optional[Dict[str, str]],
                        aspects: Optional[TaskerAspects] = DEFAULT_TASKER_ASPECTS) -> "Tasking":

    logger = None
    tasking = None

    module = import_by_name(module_name)

    if hasattr(module, tasking_name):

        logging.basicConfig(format=logging.BASIC_FORMAT, level=log_level)

        log_handler = FileHandler(logfile)
        log_handler.setLevel(log_level)
        
        logger = logging.getLogger("TASKING")
        logger.addHandler(log_handler)

        tasking_type: Type[Tasking] = getattr(module, tasking_name)

        logger.info(f"Creating tasking module_name={module_name} tasking_name={tasking_name}")

        tasking = tasking_type(worker=worker, wref=wref, tasking_id=tasking_id, parent_id=parent_id, output_dir=output_dir, 
                               logdir=logdir, logfile=logfile, logger=logger, events_endpoint=events_endpoint,
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

    PREFIX = "tasking"

    def __init__(self, worker: str, wref: str,  tasking_id: str, parent_id: str, output_dir: str, logdir: str,
                 logfile: str, logger: logging.Logger, events_endpoint: Optional[Tuple[str, int]], 
                 notify_url: Optional[str] = None, notify_headers: Optional[dict] = None,
                 aspects: Optional[TaskerAspects] = DEFAULT_TASKER_ASPECTS):

        self._worker = worker
        self._wref = wref
        self._tasking_id = tasking_id
        if self._tasking_id is None:
            self._tasking_id = str(uuid4())

        self._parent_id = parent_id
        self._output_dir = output_dir
        self._logdir = logdir
        self._logfile = logfile
        self._logger = logger
    
        self._events_host = None
        self._events_port = None

        self._events_endpoint = events_endpoint
        if self._events_endpoint is not None:
            self._events_host, self._events_port = events_endpoint

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
    def full_name(self) -> str:
        this_type = type(self)
        fname = f"{this_type.__module__}@{this_type.__name__}"
        return fname

    @property
    def result(self) -> TaskingResult:
        return self._result

    @property
    def task_status(self) -> ProgressCode:
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

    def create_tasking_result(self, tasking_id: str, tasking_name: str, parent_id: str, prefix: str) -> TaskingResult:
        """
            Called to create the 'TaskingResult' object and can be overloaded by Tasking(s) to create a custom derived
            'TaskingResult' type.
        """
        tresult = TaskingResult(tasking_id, tasking_name, parent_id, self._worker, prefix=prefix)
        return tresult

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

    def evaluate_results(self):
        """
            The `evaluate_results` method is called in order to process information to
            create a final status code for the given tasking.

            :returns: Returns the 'result_code' that is written into the tasking result.
        """
        return

    def finalize(self):
        """
            The `finalize` method is called in order to provide an opportunity for a tasking
            to finalize execution and cleanup resources as required.
        """
        self.result.finalize()

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
        
        start_fmt = format_datetime_with_fractional(self._result.start)

        begin_msg_lines = [
            f"------------------------------- TASKING BEGUN -------------------------------",
            f"  TASK_NAME: {self._result.name}",
            f"    TASK_ID: {self._result.inst_id}",
            f"  PARENT_ID: {self._result.parent_inst}",
            f"     LOGDIR: {self._logdir}",
            f"      START: {start_fmt}"
        ]

        kwparams_lines = pformat(kwparams, indent=4, width=200).splitlines(False)
        kwparams_lines = indent_lines_list(kwparams_lines, level=1, indent=10)

        begin_msg_lines.append("  KWPARAMS:")
        begin_msg_lines.extend(kwparams_lines)

        begin_msg = os.linesep.join(begin_msg_lines)

        return begin_msg

    def format_finalize_message(self):
        """
            Formats the tasking 'FINALIZE' log message.
        """

        start_fmt = format_datetime_with_fractional(self._result.start)
        stop_fmt = format_datetime_with_fractional(self._result.stop)

        finalize_msg_lines = [
            "------------------------------- TASKING FINALIZED -------------------------------",
            f"    TASK_NAME: {self._result.name}",
            f"      TASK_ID: {self._result.inst_id}",
            f"    PARENT_ID: {self._result.parent_inst}",
            f"       LOGDIR: {self._logdir}",
            f"        START: {start_fmt}",
            f"         STOP: {stop_fmt}",
            f"  RESULT_CODE: {self._result.result_code}",
        ]

        finalize_msg_lines.append("ERRORS:")
        for err in self._result.errors:
            finalize_msg_lines.extend(indent_lines_list(format_traceback_detail(err), 1))
            finalize_msg_lines.append("")

        finalize_msg_lines.append("FAILURES:")
        for fail in self._result.failures:
            finalize_msg_lines.extend(indent_lines_list(format_traceback_detail(fail), 1))
            finalize_msg_lines.append("")

        finalize_msg = os.linesep.join(finalize_msg_lines)

        return finalize_msg
    
    def format_progress_message(self, progress: dict):
        """
            Formats a tasking 'PROGRESS' log message.
        """
        prog_msg_lines = ["PROGRESS"]

        progress_lines = pformat(progress, indent=4, width=200).splitlines(False)
        progress_lines = indent_lines_list(progress_lines, level=1, indent=4)

        prog_msg_lines.extend(progress_lines)

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
            "id": self._result.inst_id,
            "parent": self._result.parent_inst,
            "worker": self._worker,
            "wref": self._wref, 
            "start": self._result.start,
            "stop": None,
            "status": str(ProgressCode.Running.value),
            "metrics": self._metrics_streams,
            "result_code": None,
            "exception" : None
        }

        return

    def mark_errored(self, err: BaseException):
        """
            Marks the tasking as having errored.  This indicates to the TaskingServer that shutdown of the
            tasking has begun.
        """
        backup_detail = traceback.format_exc()

        try:
            # Make sure we don't throw an exception formatting a traceback
            # if we do, we will end up using the backup traceback
            tbdetail = create_traceback_detail(err)

            errmsg = format_traceback_detail(tbdetail)
        except BaseException as fmterr:
            fmterr_msg = traceback.format_exc()
            self._logger.error(fmterr_msg)

            errmsg = backup_detail
        

        self._logger.error(errmsg)

        self._result.add_error(tbdetail)
    
        self.mark_progress_errored()
        self._progress_queue.put_nowait(self._current_progress)
        return

    def mark_failed(self, err: BaseException):
        tbdetail = create_traceback_detail(err)

        errmsg = format_traceback_detail(tbdetail)
        self._logger.error(errmsg)

        self._result.add_failure(tbdetail)

        self.mark_progress_failed()
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
    
    def mark_progress_failed(self):
        """
            The `mark_progress_failed` method is called to generate a :class:`ProgressInfo` failed.
        """
        self._task_status = ProgressCode.Failed
        self._current_progress.when = datetime.now()
        self._current_progress.status = ProgressCode.Failed
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
        self._current_progress = ProgressInfo(self._tasking_id, ProgressType.NumericRange, self.full_name, ProgressType.NumericRange,
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
    
    def post_event(self, event: TaskingEvent):

        if self._events_endpoint is not None:
            headers = { "Content-Type": "application/json"}
            url = f"http://{self._events_host}:{self._events_port}/"
            data = event.as_dict()

            resp = requests.post(url, headers=headers, json=data)
            if resp.status_code != HTTPStatus.ACCEPTED:
                errmsg = f"Error while posting event {event.event_name}"
                self._logger.error(errmsg)
            else:
                self._logger.info(f"Successfully posted event={event.event_name}")

        return

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

        prefix = self.PREFIX

        info_msg_lines = [
            f"Starting thread for:",
            f"    tasking name={self.full_name}",
            f"    tasking_id={self._tasking_id}"
        ]

        info_msg = os.linesep.join(info_msg_lines)

        self._logger.info(info_msg)

        self._result = self.create_tasking_result(self._tasking_id, self.full_name, self._parent_id, prefix)
        self._running = True

        try:

            self.initialize_summary()
            self.initialize_metrics()

            sgate.set()

            self.begin(kwparams)

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

                    # Evaluate results should raise an AssertionError if the tasking failed
                    # to successfully complete its tasking.
                    self.evaluate_results()

                    self.submit_progress()
                except AssertionError as aerr:
                    self.mark_failed(aerr)
                except Exception as gerr:
                    self.mark_errored(gerr)

            except Exception as evalerr:
                self.mark_errored(evalerr)

            # We still need to attempt to cleanup
            self.cleanup()

        except BaseException as finalerr:
            self.mark_errored(finalerr)

        finally:
            self.finalize()

            self._running = False

            # Pushing the result to the progress queue indicates to the
            # monitoring thread or process that this tasking is complete
            # and shutting down.
            progress_queue.put(self._result)

        return
