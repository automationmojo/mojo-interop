
from typing import List, Optional

import uuid


from mojo.interop.protocols.tasker.itaskingsequencer import ITaskingSequencer
from mojo.interop.protocols.tasker.taskeraspects import TaskerAspects, DEFAULT_TASKER_ASPECTS
from mojo.interop.protocols.tasker.taskernode import TaskerNode
from mojo.interop.protocols.tasker.taskercontroller import TaskerController


from mojo.interop.protocols.tasker.taskinggroupscope import TaskingGroupScope


class TaskingAdapter:
    """
        The 'TaskingAdapter' object marries the connectivity of a 'TaskerController' with the Test Framework result creation
        and integraton of an object that implements the 'ITaskingSequencer' protocol that allows for the integration Tasking
        results into a test frameworks result stream.

        The 'TaskingAdapter' also provides APIs for creating execution and synchronization scope objects that can be used
        by tests to efficiently coordinate and manage the creating, execution and synchronization of taskings.
    """

    def __init__(self, controller: TaskerController, sequencer: ITaskingSequencer, aspects: Optional[TaskerAspects] = DEFAULT_TASKER_ASPECTS):
        self. _controller = controller
        self._sequencer = sequencer
        self._aspects = aspects

        self._available_nodes = [node for node in self._controller.tasker_nodes]
        self._checked_out = []
        return
    

    @property
    def available_node_count(self) -> int:
        return len(self._available_nodes)


    @property
    def available_nodes(self) -> List[TaskerNode]:
        node_list = [n for n in self._available_nodes]
        return node_list


    def checkin_tasker_nodes(self, node_list: List[TaskerNode]):
        
        for node in node_list:
            self._checked_out.remove(node)
            self._available_nodes.append(node)

        return


    def checkout_tasker_nodes(self, node_count: Optional[int] = None) -> List[TaskerNode]:

        nodes = []

        nodes_available = len(self._available_nodes)

        if node_count is not None:
            if node_count > self.available_node_count:
                errmsg = f"checkout_tasker_nodes: cannot checkout more nodes than are available.  requested={node_count} available={nodes_available}"
                raise ValueError(errmsg)
            
            for i in range(node_count):
                nodes.append(self._available_nodes.pop())
        else:
            nodes = [node for node in self._available_nodes]
            self._available_nodes = []

        self._checked_out.extend(nodes)

        return nodes


    def create_tasking_group_scope(self, group_name: str, node_count: Optional[int] = None, aspects: Optional[TaskerAspects] = None) -> TaskingGroupScope:

        if aspects is None:
            aspects = self._aspects

        scope_id = str(uuid.uuid4())
        parent_id = self._sequencer.get_top_scope_id()
        recorder = self._sequencer.get_recorder()

        tgroup = self._sequencer.create_tasking_group(scope_id, group_name, parent_id)

        tnodes = self.checkout_tasker_nodes(node_count=node_count)

        tscope = TaskingGroupScope(group_name, self, self._controller, recorder, tgroup, tnodes, aspects)

        return tscope

