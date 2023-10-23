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
import os
import sys

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
                 logfile: Optional[str] = None,  logger: Optional[Logger] = None,
                 aspects: Optional[TaskerAspects] = None):

        self._task_id = task_id
        if self._task_id is None:
            self._task_id = str(uuid4())

        self._parent_id = parent_id
        self._logfile = logfile

        if logger is not None:
            self._logger = logger
        else:
            self._logger = getLogger()

        self._aspects = aspects

        self._result = None
        self._task_status = None
        
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

    def begin(self):
        self._result = TaskingResult(task_id=self._task_id, parent_id=self._parent_id)
        return
    
    def finalize(self, result_code: int):
        self._result.mark_result(result_code)
        return

    def execute(self, aspects: Optional[TaskerAspects] = None, **kwargs) -> TaskingResultPromise:

        if aspects is not None:
            self._aspects = aspects

        promise = self.monitor_scope(kwargs = kwargs)

        return promise

    def mark_progress(self, progress: TaskingProgress):
        self._progress_queue.put_nowait(progress)
        return

    def monitor_scope(self, kwargs: dict):

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

            task_proc = mpctx.Process(target=self.sequence_scope, name=task_proc_name, args=(progress_queue, kwargs), daemon=True)
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
    
    def notify_progress(self, progress: TaskingProgress):
        return

    def sequence_scope(self, progress_queue: multiprocessing.JoinableQueue, kwargs: dict):

        self._progress_queue = progress_queue

        result_code = -999

        self.begin()
        try:
            progress = self.generate_progress_start()
            self.mark_progress(progress)

            result_code = self.perform(**kwargs)
            self._result.mark_result(result_code)
            
            progress_queue.put_nowait(self._result)
        except Exception as err:
            result_code = -888
        finally:
            self.finalize(result_code)

        return

    def generate_progress_complete(self) -> TaskingProgress:
        proginfo = self._current_progress.as_dict()
        proginfo["status"] = TaskingStatus.Completed
        progress = TaskingProgress(**proginfo)
        return progress
    
    def generate_progress_errored(self) -> TaskingProgress:
        proginfo = self._current_progress.as_dict()
        proginfo["status"] = TaskingStatus.Errored
        progress = TaskingProgress(**proginfo)
        return progress

    def generate_progress_start(self) -> TaskingProgress:
        self._current_progress = TaskingProgress(0, 0, 0, TaskingStatus.Running)
        return self._current_progress

    def perform(self, **kwargs: dict):
        errmsg = "Tasking.perform method must be overloaded in derived types."
        raise NotOverloadedError(errmsg)
