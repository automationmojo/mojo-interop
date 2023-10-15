"""
.. module:: taskingresult
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`TaskingResult` class which is used to report tasking completion.

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


from typing import Optional

import os
import time

from datetime import datetime

from datetime import datetime, timedelta
from uuid import uuid4

from dataclasses import dataclass


class TaskingStatus:
    Running = "running"
    Errored = "errored"
    Completed = "completed"


@dataclass
class TaskingResult:
    """
    """

    task_id: str
    start: datetime = datetime.now()
    stop: Optional[datetime] = None
    result_code: Optional[int] = None
    parent_id: Optional[str] = None

    def mark_result(self, result_code: int):
        self._stop = datetime.now()
        self._result_code = result_code
        return



class TaskingResultPromise:

    def __init__(self, module_name: str, task_name: str, task_id: str, logfile: str) -> None:
        self._module_name = module_name
        self._task_name = task_name
        self._task_id = task_id
        self._logfile = logfile
        return
    
    @property
    def module_name(self):
        return self._module_name
    
    @property
    def task_id(self):
        return self._task_id

    @property
    def task_name(self):
        return self._task_name

    def wait(self, timeout: float, interval: float):

        finished = False

        now = datetime.now()
        start_time = now
        end_time = now + timedelta(seconds=timeout)

        while (True):

            finished = self._is_task_complete()
            if finished:
                break

            now = datetime.now()
            if now > end_time:
                break

            time.sleep(interval)

        if not finished and now > end_time:
            diff = now - start_time
            task_label = f"{self.module_name}.{self._task_name}"
            errmsg_lines = [
                f"Timeout waiting for task={task_label} id={self._task_id} start={start_time} end={end_time} now={now} diff={diff}",
                f"    LOGFILE: {self._logfile}"
            ]
            errmsg = os.linesep.join(errmsg_lines)
            raise TimeoutError(errmsg)

        return
    
    def _is_task_complete(self) -> bool:
        return
