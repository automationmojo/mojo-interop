
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


from typing import Optional, TYPE_CHECKING


import rpyc
import pickle
import weakref


from mojo.interop.protocols.tasker.taskingresult import TaskingResult, TaskingResultPromise


if TYPE_CHECKING:
    from mojo.xmods.landscaping.client.clientbase import ClientBase


TASKER_PROTOCOL_CONFIG = {
    "allow_public_attrs": True,
    "allow_pickle": True,
    "import_custom_exceptions": True,
    "allow_custom_exceptions": True
}

class TaskerNode:
    """
        The :class:`TaskerNode` object represents a remote tasker service endpoint.
    """

    def __init__(self, client: "ClientBase", ipaddr: str, port: int):
        self._client_ref = weakref.ref(client)
        self._ipaddr = ipaddr
        self._port = port
        self._rpyc_client = None
        return

    @property
    def client(self) -> "ClientBase":
        return self._client_ref()

    @property
    def ipaddr(self):
        return self._ipaddr
    
    @property
    def port(self):
        return self._port

    def archive_folder(self, *, folder_to_archive: str, dest_folder: str, archive_name: str, compression_level: int = 7) -> str:
        rmt_archive_fullpath = self._rpyc_client.root.archive_folder(folder_to_archive=folder_to_archive, dest_folder=dest_folder,
                                         archive_name=archive_name, compression_level=compression_level)
        return rmt_archive_fullpath

    def file_exists(self, *, filename: str) -> bool:
        exists = self._rpyc_client.root.file_exists(filename=filename)
        return exists
    
    def folder_exists(self, *, folder: str) -> bool:
        exists = self._rpyc_client.root.folder_exists(folder=folder)
        return exists

    def get_tasking_status(self, *, task_id: str) -> str:
        tstatus = self._rpyc_client.root.get_tasking_status(task_id=task_id)
        return tstatus
    
    def get_tasking_result(self, *, task_id: str) -> TaskingResult:
        tresult_str = self._rpyc_client.root.get_tasking_result(task_id=task_id)
        tresult = pickle.loads(tresult_str)
        return tresult

    def has_completed_and_result_ready(self, *, task_id: str):
        complete_and_ready = self._rpyc_client.root.has_completed_and_result_ready(task_id=task_id)
        return complete_and_ready

    def execute_tasking(self, *, module_name: str, tasking_name: str, **kwargs) -> TaskingResultPromise:

        if self._rpyc_client is None:
            self._connect()

        taskref_info = self._rpyc_client.root.execute_tasking(module_name=module_name, tasking_name=tasking_name, **kwargs)
        promise = TaskingResultPromise(taskref_info["module_name"], taskref_info["task_id"], taskref_info["task_name"], taskref_info["log_dir"], self)

        return promise

    def reinitialize_logging(self, *, logging_directory: Optional[str] = None,
                                      logging_level: Optional[int] = None,
                                      taskings_log_directory: Optional[str] = None,
                                      taskings_log_level: Optional[int] = None):
        
        if self._rpyc_client is None:
            self._connect()
        
        self._rpyc_client.root.reinitialize_logging(logging_directory=logging_directory, logging_level=logging_level,
                taskings_log_directory=taskings_log_directory, taskings_log_level=taskings_log_level)

        return

    def resolve_path(self, *, path) -> str:

        full_path = self._rpyc_client.root.resolve_path(path=path)
        
        return full_path

    def set_notify_parameters(self, *, notify_url: str, notify_headers: dict):
        
        if self._rpyc_client is None:
            self._connect()
        
        self._rpyc_client.root.set_notify_parameters(notify_url=notify_url, notify_headers=notify_headers)

        return

    def _connect(self):
        self._rpyc_client = rpyc.connect(self._ipaddr, self._port, keepalive=True, config=TASKER_PROTOCOL_CONFIG)
        return


class TaskerClientNode(TaskerNode):

    def __init__(self, client: "ClientBase", ipaddr: str, port: int):
        self._client_ref = weakref.ref(client)
        super().__init__(ipaddr, port)
        return

    @property
    def client(self) -> "ClientBase":
        return self._client_ref()