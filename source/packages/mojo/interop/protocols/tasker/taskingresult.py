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


from typing import Any, Optional

import os
import time

from datetime import datetime

from datetime import datetime, timedelta
from uuid import uuid4

from dataclasses import dataclass, asdict

DEFAULT_WAIT_TIMEOUT = 600
DEFAULT_WAIT_INTERVAL = 5

class TaskingStatus:
    Completed = "Completed"
    Errored = "Errored"
    NotStarted = "NotStarted"
    Paused = "Paused"
    Running = "Running"
    

@dataclass
class TaskingResult:
    """
    """

    task_id: str
    start: datetime = datetime.now()
    stop: Optional[datetime] = None
    result_code: Optional[int] = None
    parent_id: Optional[str] = None
    exception: Optional[Exception] = None

    def mark_result(self, result_code: int, exception: Optional[Exception] = None):

        if self.stop is None:
            self.stop = datetime.now()

        # It is possible for us to have a chain of result codes being set if errors are being
        # encountered in teardown methods.
        if self.result_code is None:
            self.result_code = result_code
        elif isinstance(self.result_code, list):
            self.result_code.append(result_code)
        else:
            self.result_code = [self.result_code, result_code]

        if exception is not None:
            self.exception = exception

        return


@dataclass
class TaskingRef:
    
    module_name: str
    task_id: str
    task_name: str
    log_file: str

    def as_dict(self):
        rtnval = asdict(self)
        return rtnval


class TaskingResultPromise:

    def __init__(self, module_name: str, task_id: str, task_name: str, log_file: str, client: Any):
        self._module_name = module_name
        self._task_id = task_id
        self._task_name = task_name
        self._log_file = log_file
        self._client = client
        return

    @property
    def log_file(self):
        return self._log_file

    @property
    def module_name(self):
        return self._module_name
    
    @property
    def task_id(self):
        return self._task_id
    
    @property
    def task_name(self):
        return self._task_name

    def wait(self, timeout: float=DEFAULT_WAIT_TIMEOUT, interval: float=DEFAULT_WAIT_INTERVAL):

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

        rtnval = False

        status = self._client.root.get_tasking_status(task_id=self._task_id)
        if status == TaskingStatus.Completed:
            rtnval = True

        return rtnval
