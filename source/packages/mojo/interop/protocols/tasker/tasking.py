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


from typing import Optional, Tuple

import multiprocessing
import requests
import sys
import threading

from dataclasses import dataclass
from logging import Logger, getLogger
from uuid import uuid4

from mojo.errors.exceptions import NotOverloadedError
from mojo.interop.protocols.tasker.taskingresult import TaskingStatus, TaskingResult, TaskingResultPromise
from mojo.interop.protocols.tasker.taskingprogress import TaskingProgress
from mojo.interop.protocols.tasker.taskeraspects import TaskerAspects

@dataclass
class TaskingIdentity:
    module_name: str
    tasking_name: str

    def as_tuple(self) -> Tuple[str, str]:
        return self.module_name, self.tasking_name


class Tasking:
    """
    """

    def __init__(self, task_id: Optional[str] = None, parent_id: Optional[str] = None,
                 notify_url: Optional[str] = None, notify_headers: Optional[dict] = None,
                 logfile: Optional[str] = None,  logger: Optional[Logger] = None,
                 aspects: Optional[TaskerAspects] = None):

        self._task_id = task_id
        if self._task_id is None:
            self._task_id = str(uuid4())

        self._parent_id = parent_id

        self._notify_url = notify_url
        self._notify_headers = notify_headers

        self._logfile = logfile
        if logger is not None:
            self._logger = logger
        else:
            self._logger = getLogger()

        self._aspects = aspects
        self._kwparams: dict = None

        self._result = None
        self._exception = None

        self._task_status = TaskingStatus.NotStarted
        self._running = False
        self._pause_gate = threading.Event()
        
        # Progress queue is used by the task process to push back progress and
        # results.
        self._current_progress = None
        self._progress_queue: multiprocessing.JoinableQueue = None

        return

    @classmethod
    def get_identity(cls) -> TaskingIdentity:
        module_name = cls.__module__
        tasking_name = cls.__name__
        identity = TaskingIdentity(module_name=module_name, tasking_name=tasking_name)
        return identity

    def begin(self, kwparams: dict):
        """
            The `begin` method is called in order to stash the `kwparams` on the tasking instance
            and to create the result container.
        """
        self._kwparams = kwparams
        self._result = TaskingResult(task_id=self._task_id, parent_id=self._parent_id)
        return

    def execute(self, aspects: Optional[TaskerAspects] = None, **kwargs) -> TaskingResultPromise:
        """
            The `execute` method is called by the tasking service in order to trigger the execution
            of the task.
        """
        if aspects is not None:
            self._aspects = aspects

        promise = self._monitor_scope(kwargs = kwargs)

        return promise

    def evaluate_results(self) -> int:
        """
            The `evaluate_results` method is called in order to process information to
            create a final status code for the given tasking.
        """
        errmsg = "Tasking.evaluate_results method must be overloaded in derived types."
        raise NotOverloadedError(errmsg)

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

    def generate_progress_complete(self) -> TaskingProgress:
        """
            The `generate_progress_complete` method is called to generate a :class:`TaskingProgress` completed.
        """
        self._current_progress.status = TaskingStatus.Completed
        return self._current_progress
    
    def generate_progress_errored(self) -> TaskingProgress:
        """
            The `generate_progress_errored` method is called to generate a :class:`TaskingProgress` errored.
        """
        self._current_progress.status = TaskingStatus.Errored
        return self._current_progress
    
    def generate_progress_paused(self) -> TaskingProgress:
        """
            The `generate_progress_paused` method is called to generate a :class:`TaskingProgress` paused.
        """
        self._current_progress.status = TaskingStatus.Paused
        return self._current_progress

    def generate_progress_start(self) -> TaskingProgress:
        """
            The `generate_progress_start` method that is called to generate a :class:`TaskingProgress` running.
        """
        self._current_progress = TaskingProgress(0, 0, 0, TaskingStatus.Running)
        return self._current_progress

    def mark_errored(self):
        """
            Marks the tasking as having errored.  This indicates to the TaskingServer that shutdown of the
            tasking has begun.
        """
        progress = self.generate_progress_errored()
        self._progress_queue.put_nowait(progress)
        return

    def mark_progress(self, progress: TaskingProgress):
        """
            Marks the tasking as having made progress on some activity so the TaskingServer 'hang' detection
            does not trigger an inactivity timeout shutdown of the tasking.
        """
        self._progress_queue.put_nowait(progress)
        return

    def notify_progress(self, progress: TaskingProgress):
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

            requests.post(self._notify_url, json=body, headers=headers)

        return

    def pause(self):
        """
            Pauses the tasking loop
        """
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

    def result(self):
        """
            Resumes the tasking loop
        """
        self._pause_gate.set()
        return

    def _monitor_scope(self, kwargs: dict):

        this_type = type(self)

        module_name = this_type.__module__
        task_name = this_type.__name__

        promise = None

        id_tail = self._task_id[len(self._task_id) - 8:]
        task_proc_name = f'task-{id_tail}'

        try:

            mpctx = multiprocessing.get_context('fork')
            progress_queue = mpctx.JoinableQueue()
            
            result_timeout = None
            if self._aspects is not None and self._aspects.completion_timeout is not None:
                result_timeout = self._aspects.completion_interval

            promise = TaskingResultPromise(module_name, task_name, self._task_id, self._logfile)

            task_proc = mpctx.Process(target=self._sequence_scope, name=task_proc_name, args=(progress_queue, kwargs), daemon=True)
            task_proc.start()

            while(True):
                progress = progress_queue.get(block=True, timeout=result_timeout)
                if isinstance(progress, TaskingResult):
                    self._result = progress
                    break

                self.notify_progress(progress)

            # Only attempt to join the the child process for shutdown if we received a result
            task_proc.join()

        except TimeoutError as toerr:
            pass
        except Exception as generr:
            exc_info = sys.exc_info()
            self._logger.exception("Exception while executing task.", exc_info=exc_info)

        return promise

    def _sequence_scope(self, progress_queue: multiprocessing.JoinableQueue, kwparams: dict):

        self._progress_queue = progress_queue

        self._result_code = None

        self.begin(kwparams)
        self._task_status = TaskingStatus.Running

        try:

            try:

                try:
                    progress = self.generate_progress_start()
                    self.mark_progress(progress)

                    while self._task_status == TaskingStatus.Running or self._task_status == TaskingStatus.Paused:

                        if self._task_status == TaskingStatus.Paused:
                            progress = self.generate_progress_paused()
                            self.mark_progress(progress)

                            self._pause_gate.wait()

                        cont = self.fire_perform()
                        if not cont:
                            break
                    
                    progress = self.generate_progress_complete()
                    self.mark_progress(progress)

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
            
            self._result.mark_result(self._result_code)

            # We still need to attempt to cleanup
            self.finalize()

        except Exception as finalerr:
            if self._result_code is None:
                    self._result_code = -888
                    self._result.mark_result(self._result_code)

            if self._exception is not None:
                try:
                    raise finalerr from self._exception
                except Exception as comberr:
                    self._exception = comberr
            else:
                self._exception = finalerr

            self.mark_errored()

        finally:
            # Pushing the result to the progress queue indicates to the
            # monitoring thread or process that this tasking is complete
            # and shutting down.
            progress_queue.put_nowait(self._result)

        return
