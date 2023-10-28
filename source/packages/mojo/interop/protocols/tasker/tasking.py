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

import logging
import requests
import threading

from dataclasses import dataclass
from logging.handlers import WatchedFileHandler

from uuid import uuid4

from mojo.errors.exceptions import NotOverloadedError

from mojo.results.model.progressinfo import ProgressInfo, ProgressType
from mojo.results.model.progresscode import ProgressCode

from mojo.xmods.ximport import import_by_name

from mojo.interop.protocols.tasker.taskingresult import TaskingResult
from mojo.interop.protocols.tasker.taskeraspects import TaskerAspects, DEFAULT_TASKER_ASPECTS


def instantiate_tasking(module_name: str, tasking_name: str, task_id: str, parent_id: str, logfile: str,
                        logdir: str, log_level: int, notify_url: Optional[str], notify_headers: Optional[Dict[str, str]],
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

    def begin(self, kwparams: dict):
        """
            The `begin` method is called in order to stash the `kwparams` on the tasking instance
            and to create the result container.
        """
        self._kwparams = kwparams
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
        """
        return 0

    def finalize(self):
        """
            The `finalize` method is called in order to provide an opportunity for a tasking
            to finalize execution and cleanup resources as required.
        """
        return
    
    def fire_perform(self):
        """
            The `fire_peform` allows for modification of the calling of the perform method.
        """
        return self.perform()

    def mark_progress_complete(self):
        """
            The `mark_progress_complete` method is called to generate a :class:`ProgressInfo` completed.
        """
        self._task_status = ProgressCode.Completed
        self._current_progress.status = ProgressCode.Completed
        return

    def mark_progress_errored(self):
        """
            The `mark_progress_errored` method is called to generate a :class:`ProgressInfo` errored.
        """
        self._task_status = ProgressCode.Errored
        self._current_progress.status = ProgressCode.Errored
        return
    
    def mark_progress_paused(self):
        """
            The `mark_progress_paused` method is called to generate a :class:`ProgressInfo` paused.
        """
        self._task_status = ProgressCode.Paused
        self._current_progress.status = ProgressCode.Paused
        return
    
    def mark_progress_running(self):
        """
            The `mark_progress_running` method is called to generate a :class:`ProgressInfo` running.
        """
        self._task_status = ProgressCode.Running
        self._current_progress.status = ProgressCode.Running
        return

    def mark_progress_start(self):
        """
            The `mark_progress_start` method that is called to generate a :class:`ProgressInfo` running.
        """
        self._task_status = ProgressCode.Running
        self._current_progress = ProgressInfo(self._task_id, ProgressType.NumericRange, self.full_name, 0, 0, 0, ProgressCode.Running, {})
        return

    def mark_errored(self):
        """
            Marks the tasking as having errored.  This indicates to the TaskingServer that shutdown of the
            tasking has begun.
        """
        self.mark_progress_errored()
        self._progress_queue.put_nowait(self._current_progress)
        return

    def submit_progress(self):
        """
            Submits that the tasking as having made progress on some activity so the TaskingServer 'hang' detection
            does not trigger an inactivity timeout shutdown of the tasking.
        """
        self._progress_queue.put_nowait(self._current_progress)
        self.notify_progress(self._current_progress)
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

    def perform(self) -> bool:
        """
            The `perform` method is overloaded by derived tasking types in order to implement
            the performance of a unit of work.

            :returns: Returns a bool indicating if 'perform' should be called again in order
                      to complete more work.
        """
        errmsg = "Tasking.perform method must be overloaded in derived types."
        raise NotOverloadedError(errmsg)

    def _task_thread_entry(self, sgate: threading.Event, progress_queue: multiprocessing.JoinableQueue, kwparams: dict):

        # Update our local in process copy of these queues, because we have forked
        self._progress_queue = progress_queue

        self._result = TaskingResult(task_id=self._task_id, parent_id=self._parent_id)
        self._running = True

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
            self.finalize()

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

            self._running = False

            # Pushing the result to the progress queue indicates to the
            # monitoring thread or process that this tasking is complete
            # and shutting down.
            progress_queue.put(self._result)

        return
