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
from mojo.interop.protocols.tasker.taskingresult import TaskingStatus, TaskingResult
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

        self._task_status = TaskingStatus.NotStarted
        self._running = False
        self._shutdown = False
        self._pause_gate = threading.Event()
        
        # The following variables are shared between process but must be updated in the parent process
        # when progress or state comes back from the child process
        self._result = None
        self._exception = None

        # The following variables are shared between process and must be updated in the child when it is
        # spawned so it gets the local end of the object
        self._command_queue: multiprocessing.Queue = None

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

    def execute(self, kwparams: dict, aspects: Optional[TaskerAspects] = None):
        """
            The `execute` method is called by the tasking service in order to trigger the execution
            of the task.
        """
        if aspects is not None:
            self._aspects = aspects

        self._monitor_scope(kwparams = kwparams)

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
            The `mark_progress_complete` method is called to generate a :class:`TaskingProgress` completed.
        """
        self._current_progress.status = TaskingStatus.Completed
        return

    def mark_progress_errored(self):
        """
            The `mark_progress_errored` method is called to generate a :class:`TaskingProgress` errored.
        """
        self._current_progress.status = TaskingStatus.Errored
        return
    
    def mark_progress_paused(self):
        """
            The `mark_progress_paused` method is called to generate a :class:`TaskingProgress` paused.
        """
        self._current_progress.status = TaskingStatus.Paused
        return
    
    def mark_progress_running(self):
        """
            The `mark_progress_running` method is called to generate a :class:`TaskingProgress` running.
        """
        self._current_progress.status = TaskingStatus.Running
        return

    def mark_progress_start(self):
        """
            The `mark_progress_start` method that is called to generate a :class:`TaskingProgress` running.
        """
        self._current_progress = TaskingProgress(0, 0, 0, TaskingStatus.Running)
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

            try:
                requests.post(self._notify_url, json=body, headers=headers)
            except Exception as xcpt:
                print(xcpt)
                self._logger.error(f"Failure during notification to url='{self._notify_url}'")

        return

    def effect_pause(self):
        """
            Sends a Pause command to the remote tasking
        """
        self._command_queue.put("pause")
        return
    
    def effect_resume(self):
        """
            Resumes the tasking loop
        """
        self._command_queue.put("resume")
        return

    def effect_shutdown(self):
        """
            Sends a Shutdown command to the remote tasking
        """
        self._command_queue.put("shutdown")
        return
    
    def handle_pause(self):
        """
            Sends a Pause command to the remote tasking
        """
        self._task_status = TaskingStatus.Paused
        self._pause_gate.clear()
        return
    
    def handle_resume(self):
        """
            Resumes the tasking loop
        """
        self._task_status = TaskingStatus.Running
        self._pause_gate.set()
        return
    
    def handle_shutdown(self):
        """
            Sends a Shutdown command to the remote tasking
        """
        self._running = False
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

    def _monitor_scope(self, kwparams: dict):

        id_tail = self._task_id[len(self._task_id) - 8:]
        task_proc_name = f'task-{id_tail}'

        try:

            mpctx = multiprocessing.get_context('fork')

            self._command_queue = mpctx.Queue()
            progress_queue = mpctx.JoinableQueue()
            
            result_timeout = None
            if self._aspects is not None and self._aspects.completion_timeout is not None:
                result_timeout = self._aspects.completion_interval

            task_proc = mpctx.Process(target=self._sequence_scope, name=task_proc_name, args=(self._command_queue, progress_queue, kwparams), daemon=True)
            task_proc.start()

            while(True):
                progress: TaskingProgress = progress_queue.get(block=True, timeout=result_timeout)
                if isinstance(progress, TaskingResult):
                    result: TaskingResult = progress
                    
                    self._exception = result.exception
                    self._result = result

                    if self._exception is not None:
                        self._task_status = TaskingStatus.Errored
                    else:
                        self._task_status = TaskingStatus.Completed
                    
                    break

                self._task_status = progress.status

                self.notify_progress(progress)

            # Only attempt to join the the child process for shutdown if we received a result
            task_proc.join()

        except TimeoutError as toerr:
            pass
        except Exception as generr:
            exc_info = sys.exc_info()
            self._logger.exception("Exception while executing task.", exc_info=exc_info)

        return

    def _effect_dispatcher_entry(self):

        while self._running:

            cmd = self._command_queue.get()

            if cmd == "pause":
                self.handle_pause()
            elif cmd == "resume":
                self.handle_resume()
            elif cmd == "shutdown":
                self.handle_shutdown()
                break

        return

    def _sequence_scope(self, command_queue: multiprocessing.Queue, progress_queue: multiprocessing.JoinableQueue, kwparams: dict):

        # Update our local in process copy of these queues, because we have forked
        self._command_queue = command_queue
        self._progress_queue = progress_queue

        self._result_code = None

        self._running = True

        eth = threading.Thread(target=self._effect_dispatcher_entry, name="effect-dispatcher", daemon=True)
        eth.start()

        self._result = TaskingResult(task_id=self._task_id, parent_id=self._parent_id)
        self.begin(kwparams)
        self._task_status = TaskingStatus.Running

        try:

            try:

                try:
                    self.mark_progress_start()
                    self.submit_progress()

                    while self._running:

                        if self._task_status == TaskingStatus.Paused:
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

            # Pushing the result to the progress queue indicates to the
            # monitoring thread or process that this tasking is complete
            # and shutting down.
            progress_queue.put_nowait(self._result)

        return
