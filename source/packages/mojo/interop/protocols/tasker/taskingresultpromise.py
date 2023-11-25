"""
.. module:: taskingresultpromise
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`TaskingResultPromise` class which is used to report tasking completion.

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


from typing import TYPE_CHECKING

import os
import time

from datetime import datetime

from datetime import datetime, timedelta

from dataclasses import dataclass, asdict

DEFAULT_WAIT_TIMEOUT = 600
DEFAULT_WAIT_INTERVAL = 5


if TYPE_CHECKING:
    from mojo.interop.protocols.tasker.taskernode import TaskerNode


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

    def __init__(self, module_name: str, tasking_id: str, task_name: str, log_dir: str, node: "TaskerNode"):
        self._module_name = module_name
        self._tasking_id = tasking_id
        self._task_name = task_name
        self._log_dir = log_dir
        self._node = node
        return

    @property
    def log_dir(self):
        return self._log_dir

    @property
    def module_name(self):
        return self._module_name
    
    @property
    def tasking_id(self):
        return self._tasking_id
    
    @property
    def task_name(self):
        return self._task_name

    def get_result(self):
        rtnval = self._node.get_tasking_result(tasking_id=self._tasking_id)
        return rtnval

    def wait(self, timeout: float=DEFAULT_WAIT_TIMEOUT, interval: float=DEFAULT_WAIT_INTERVAL):

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

            finished = self._is_task_complete()
            if finished:
                break

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
    
    def _is_task_complete(self) -> bool:

        rtnval = self._node.has_completed_and_result_ready(tasking_id=self._tasking_id)

        return rtnval

