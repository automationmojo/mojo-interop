"""
.. module:: taskercontroller
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: The :class:`TaskerController` package contains the controller object used to create a distributed
               network of :class:`TaskerService` objects.

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


from typing import List, Optional, Type, Union

from mojo.errors.exceptions import NotOverloadedError, SemanticError

from mojo.interop.protocols.tasker.taskeraspects import TaskerAspects
from mojo.interop.protocols.tasker.tasking import Tasking, TaskingIdentity
from mojo.interop.protocols.tasker.taskernode import TaskerNode
from mojo.interop.protocols.tasker.taskingresult import TaskingResultPromise
from mojo.interop.protocols.tasker.taskerservice import TaskerService
from mojo.interop.protocols.tasker.taskerservermanager import TaskerServerManager, spawn_tasking_server_process

from mojo.xmods.landscaping.client.clientbase import ClientBase


TASKER_PORT = 8686

class TaskerController:
    """
        The :class:`TaskerController` object lets you startup and control task processing across
        a collection of clients.
    """

    def __init__(self, logging_directory: Optional[str] = None, aspects: Optional[TaskerAspects] = None):
        self._logging_directory = logging_directory
        self._aspects = aspects

        self._tasker_nodes: List[TaskerNode] = []
        self._network_started = False
        return

    @property
    def tasker_nodes(self):
        return self._tasker_nodes

    def execute_task_on_all_nodes(self, *, tasking: Union[TaskingIdentity, Type[Tasking]], parent_id: str = None, aspects: Optional[TaskerAspects] = None, **kwargs) -> List[TaskingResultPromise]:

        if aspects is None:
            aspects = self._aspects

        promise_list = []

        if not isinstance(tasking, TaskingIdentity):
            tasking = tasking.get_identity()
        module_name, tasking_name = tasking.as_tuple()

        for node in self._tasker_nodes:
            promise = node.execute_tasking(module_name=module_name, tasking_name=tasking_name, parent_id=parent_id, aspects=aspects, **kwargs)
            promise_list.append(promise)

        return promise_list

    def execute_task_on_node(self, nindex: int, *, tasking: Union[TaskingIdentity, Type[Tasking]], parent_id: str = None, aspects: Optional[TaskerAspects] = None, **kwargs) -> TaskingResultPromise:

        if aspects is None:
            aspects = self._aspects

        promise = None

        if not isinstance(tasking, TaskingIdentity):
            tasking = tasking.get_identity()
        module_name, tasking_name = tasking.as_tuple()
        
        node_count = len(self._tasker_nodes)
        if nindex < node_count:
            node = self._tasker_nodes[nindex]
            promise = node.execute_tasking(module_name=module_name, tasking_name=tasking_name, parent_id=parent_id, aspects=aspects, **kwargs)
        else:
            errmsg = f"The specified node index nindex={nindex} is out of range. min=0 max={node_count}"
            raise IndexError(errmsg)
        
        return promise

    def start_task_network(self):
        """
        """
        raise NotOverloadedError("The 'start_task_network' method must be overloaded.")


class ProcessTaskerController(TaskerController):

    def __init__(self, logging_directory: Optional[str] = None, aspects: Optional[TaskerAspects] = None):
        super().__init__(logging_directory=logging_directory, aspects=aspects)

        self._svr_manager: List[TaskerServerManager] = []
        self._svr_proxies: List[TaskerService] = []
        return

    def start_tasker_network(self, node_count=5, notify_url: Optional[str] = None, notify_headers: Optional[dict] = None):
        """
        """

        if self._network_started:
            errmsg = "A task network has already been started."
            raise SemanticError(errmsg)

        self._network_started = True

        for _ in range(node_count):
            svr_mgr, tasking_svr_proxy = spawn_tasking_server_process(('0.0.0.0', 0), logging_directory=self._logging_directory)

            tasking_svr_proxy.start()

            self._svr_manager.append(svr_mgr)
            self._svr_proxies.append(tasking_svr_proxy)

            ipaddr, port = tasking_svr_proxy.get_service_endpoint()

            node = TaskerNode(ipaddr=ipaddr, port=port)
            
            if notify_url is not None:
                node.set_notify_parameters(notify_url=notify_url, notify_headers=notify_headers)

            self._tasker_nodes.append(node)

        return


class ClientTaskerController(TaskerController):

    def __init__(self, logging_directory: Optional[str] = None, aspects: Optional[TaskerAspects] = None):
        super().__init__(logging_directory=logging_directory, aspects=aspects)
        return

    def start_tasker_network(self, clients: List[ClientBase], notify_url: Optional[str] = None, notify_headers: Optional[dict] = None):
        """
        """

        if self._network_started:
            errmsg = "A task network has already been started."
            raise SemanticError(errmsg)

        self._network_started = True

        for cl in clients:

            node = TaskerNode(ipaddr=cl.ipaddr, port=TASKER_PORT)
            
            if notify_url is not None:
                node.set_notify_parameters(notify_url=notify_url, notify_headers=notify_headers)

            self._tasker_nodes.append(node)

        return
