"""
.. module:: taskingresultpromise
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`TaskingResultPromise` class which is used to report tasking completion.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []



from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

import logging
import os
import time

from datetime import datetime, timedelta

from dataclasses import dataclass, asdict

DEFAULT_WAIT_TIMEOUT = 600
DEFAULT_WAIT_INTERVAL = 5

from mojo.results.model.taskingresult import TaskingResult
from mojo.results.model.progressinfo import ProgressInfo

from mojo.interop.protocols.tasker.taskingevent import TaskingEvent
from mojo.interop.protocols.tasker.taskingprogressmonitor import TaskingProgressMonitor

if TYPE_CHECKING:
    from mojo.interop.protocols.tasker.taskernode import TaskerNode


logger = logging.getLogger()

@dataclass
class TaskingRef:
    
    module_name: str
    tasking_id: str
    task_name: str
    log_dir: str

    def as_dict(self):
        rtnval = asdict(self)
        return rtnval


class TaskingResultPromise:

    def __init__(self, client, responder, module_name: str, tasking_id: str, task_name: str, log_dir: str,
                 session_id: str, node: "TaskerNode", progress_monitor: Optional[TaskingProgressMonitor] = None):
        self._client = client
        self._responder = responder
        self._module_name = module_name
        self._tasking_id = tasking_id
        self._task_name = task_name
        self._log_dir = log_dir
        self._session_id = session_id
        self._node = node

        self._progress_monitor = progress_monitor
        return

    def __del__(self):

        if self._progress_monitor is not None:
            self._progress_monitor.release(self._tasking_id)

        # Keep the task run client open until this object
        # is destroyed in case there are NetRef objects that are
        # being used by the remote end.
        if self._responder is not None:
            try:
                self._responder.stop()
                self._client.close()
            except:
                pass

        return

    @property
    def log_dir(self) -> str:
        return self._log_dir

    @property
    def module_name(self) -> str:
        return self._module_name
    
    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def tasking_id(self) -> str:
        return self._tasking_id
    
    @property
    def task_name(self) -> str:
        return self._task_name

    def cancel(self):
        """
            Cancel the assocated tasking.
        """
        self._node.cancel_tasking(tasking_id=self._tasking_id)
        return

    def call_tasking_method(self, method_name: str, *args, **kwargs) -> Any:
        """
            Calls the method on the tasking associated with this :class:`TaskingResultPromise` object.

            :param method_name: The name of the method to call on the tasking.
            :param *args: A list of variable positional arguements.
            :param **kwargs: A dictionary of the key-word argurements for the function.

            :returns: Returns the result returned by the remote method.
        """
        
        rtnval = self._node.call_tasking_method(tasking_id=self._tasking_id, method_name=method_name, args=args, kwargs=kwargs)

        return rtnval

    def get_events(self) -> List[TaskingEvent]:
        """
            Get the events that have been posted by the associated tasking.
        """
        rtnval = self._node.get_tasking_events(tasking_id=self._tasking_id)
        
        return rtnval

    def get_result(self) -> TaskingResult:
        """
            Get the result of the associated tasking.
        """
        rtnval = self._node.get_tasking_result(tasking_id=self._tasking_id)
        return rtnval

    def get_progress(self) -> ProgressInfo:
        """
            Used by TaskingGroupScope and other group wait methods to probe for progress.
        """

        progress = self._node.get_tasking_progress(tasking_id=self._tasking_id)

        return progress

    def wait(self, timeout: float=DEFAULT_WAIT_TIMEOUT, interval: float=DEFAULT_WAIT_INTERVAL):
        """
            The 'wait' method on the promise object is used to wait on a single tasking to complete
            and will block until the tasking is complete or until a timeout has occured.  To wait
            on a group of tasks, use the wait method on `TaskingGroupScope` to wait on multiple
            tasks simultaneously.

            :param timeout: A period of time to wait for the completion of the tasking.
            :param interval: An interval to sleep between checks for completion.

            :raises: :class:`TimeoutError`
        """
        
        finished = False

        now = datetime.now()
        start_time = now

        end_time = None
        if timeout is not None:
            end_time = now + timedelta(seconds=timeout)

        if interval is None:
            # 'interval' cannot be None
            interval = DEFAULT_WAIT_INTERVAL

        while (True):

            try:
                finished = self.is_task_complete()
                if finished:
                    break
            except EOFError as ferr:
                # rpyc might throw an EOFError here, absorb and retry
                # until we timeout
                errmsg = "'EOFError' encountered while waiting on task to complete"
                logger.info(errmsg)

            now = datetime.now()
            if end_time is not None and now > end_time:
                break

            time.sleep(interval)

        if not finished:
            if end_time is not None:
                diff = now - start_time
                task_label = f"{self.module_name}.{self._task_name}"
                errmsg_lines = [
                    f"Timeout waiting for task={task_label} id={self._tasking_id} start={start_time} end={end_time} now={now} diff={diff}",
                    f"    LOGDIR: {self._logdir}"
                ]
                errmsg = os.linesep.join(errmsg_lines)
                raise TimeoutError(errmsg)
            else:
                errmsg = "Timeout was not set but we exited before finished was 'True'."
                raise RuntimeError(errmsg)

        return
    
    def is_task_complete(self) -> bool:
        """
            Returns a boolean value indicating if the associated tasking is complete.

            ..node:  This is intentionally implemented as a method and not a property in order to ensure that
                     we do not make cross process or across network calls from an object property.
        """

        rtnval = self._node.has_completed_and_result_ready(tasking_id=self._tasking_id)

        return rtnval
    
