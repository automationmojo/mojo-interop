
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


from mojo.results.model.taskingresult import TaskingResult

from mojo.interop.protocols.tasker.taskingresultpromise import TaskingResultPromise
from mojo.interop.protocols.tasker.taskeraspects import TaskerAspects, DEFAULT_TASKER_ASPECTS

if TYPE_CHECKING:
    from mojo.landscaping.client.clientbase import ClientBase


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

    def __init__(self, ipaddr: str, port: int, aspect: TaskerAspects=DEFAULT_TASKER_ASPECTS):
        self._ipaddr = ipaddr
        self._port = port
        self._aspects = aspect
        return

    @property
    def ipaddr(self):
        return self._ipaddr
    
    @property
    def port(self):
        return self._port

    def archive_folder(self, *, folder_to_archive: str, dest_folder: str, archive_name: str, compression_level: int = 7) -> str:
        
        client = self._create_connection()

        try:
            rmt_archive_fullpath = client.root.archive_folder(folder_to_archive=folder_to_archive, dest_folder=dest_folder,
                                         archive_name=archive_name, compression_level=compression_level)
        finally:
            client.close()
        
        return rmt_archive_fullpath

    def file_exists(self, *, filename: str) -> bool:

        client = self._create_connection()

        try:
            exists = client.root.file_exists(filename=filename)
        finally:
            client.close()
        
        return exists
    
    def folder_exists(self, *, folder: str) -> bool:

        client = self._create_connection()

        try:
            exists = client.root.folder_exists(folder=folder)
        finally:
            client.close()
        
        return exists

    def get_tasking_status(self, *, tasking_id: str) -> str:

        client = self._create_connection()

        try:
            tstatus = client.root.get_tasking_status(tasking_id=tasking_id)
        finally:
            client.close()
        
        return tstatus
    
    def get_tasking_result(self, *, tasking_id: str) -> TaskingResult:

        client = self._create_connection()

        try:
            tresult_str = client.root.get_tasking_result(tasking_id=tasking_id)
            tresult = pickle.loads(tresult_str)
        finally:
            client.close()
        
        return tresult

    def has_completed_and_result_ready(self, *, tasking_id: str):

        client = self._create_connection()

        try:
            complete_and_ready = client.root.has_completed_and_result_ready(tasking_id=tasking_id)
        finally:
            client.close()
        
        return complete_and_ready

    def execute_tasking(self, *, module_name: str, tasking_name: str, **kwargs) -> TaskingResultPromise:

        client = self._create_connection()

        try:
            taskref_info = client.root.execute_tasking(worker=self._ipaddr, module_name=module_name, tasking_name=tasking_name, **kwargs)
            promise = TaskingResultPromise(taskref_info["module_name"], taskref_info["tasking_id"], taskref_info["task_name"],
                                        taskref_info["log_dir"], self)
        finally:
            client.close()

        return promise

    def reinitialize_logging(self, *, logging_directory: Optional[str] = None,
                                      logging_level: Optional[int] = None,
                                      taskings_log_directory: Optional[str] = None,
                                      taskings_log_level: Optional[int] = None):
        
        client = self._create_connection()
        
        try:
            client.root.reinitialize_logging(logging_directory=logging_directory, logging_level=logging_level,
                    taskings_log_directory=taskings_log_directory, taskings_log_level=taskings_log_level)
        finally:
            client.close()

        return

    def resolve_path(self, *, path) -> str:

        client = self._create_connection()

        try:
            full_path = client.root.resolve_path(path=path)
        finally:
            client.close()
        
        return full_path

    def set_notify_parameters(self, *, notify_url: str, notify_headers: dict):
        
        client = self._create_connection()
        
        try:
            client.root.set_notify_parameters(notify_url=notify_url, notify_headers=notify_headers)
        finally:
            client.close()

        return

    def _create_connection(self):
        client = rpyc.connect(self._ipaddr, self._port, keepalive=True, config=TASKER_PROTOCOL_CONFIG)
        return client


class TaskerClientNode(TaskerNode):

    def __init__(self, client: "ClientBase", ipaddr: str, port: int):
        self._client_ref = weakref.ref(client)
        super().__init__(ipaddr, port)
        return

    @property
    def client(self) -> "ClientBase":
        return self._client_ref()