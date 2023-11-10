
"""
.. module:: taskernode
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: The :class:`TaskerNode` object that is used to.

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


import rpyc
import pickle


from mojo.interop.protocols.tasker.taskingresult import TaskingResult, TaskingResultPromise


class TaskerNode:
    """
        The :class:`TaskerNode` object represents a remote tasker service endpoint.
    """

    def __init__(self, ipaddr: str, port: int):
        self._ipaddr = ipaddr
        self._port = port
        self._client = None
        return

    @property
    def ipaddr(self):
        return self._ipaddr
    
    @property
    def port(self):
        return self._port

    def get_tasking_status(self, *, task_id: str) -> str:
        tstatus = self._client.root.get_tasking_status(task_id=task_id)
        return tstatus
    
    def get_tasking_result(self, *, task_id: str) -> TaskingResult:
        tresult_str = self._client.root.get_tasking_result(task_id=task_id)
        tresult = pickle.loads(tresult_str)
        return tresult

    def execute_tasking(self, *, module_name: str, tasking_name: str, **kwargs) -> TaskingResultPromise:

        if self._client is None:
            self._connect()

        taskref_info = self._client.root.execute_tasking(module_name=module_name, tasking_name=tasking_name, **kwargs)
        promise = TaskingResultPromise(taskref_info["module_name"], taskref_info["task_id"], taskref_info["task_name"], taskref_info["log_dir"], self)

        return promise

    def reinitialize_logging(self, *, logging_directory: Optional[str] = None,
                                      logging_level: Optional[int] = None,
                                      taskings_log_directory: Optional[str] = None,
                                      taskings_log_level: Optional[int] = None):
        
        if self._client is None:
            self._connect()
        
        self._client.root.set_logging_parameters(logging_directory=logging_directory, logging_level=logging_level,
                taskings_log_directory=taskings_log_directory, taskings_log_level=taskings_log_level)

        return

    def set_notify_parameters(self, *, notify_url: str, notify_headers: dict):
        
        if self._client is None:
            self._connect()
        
        self._client.root.set_notify_parameters(notify_url=notify_url, notify_headers=notify_headers)

        return

    def _connect(self):
        self._client = rpyc.connect(self._ipaddr, self._port, keepalive=True, config={'allow_public_attrs': True})
        return
