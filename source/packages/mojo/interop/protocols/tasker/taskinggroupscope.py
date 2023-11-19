from typing import List, Optional, Type, Union, TYPE_CHECKING

import weakref

from mojo.errors.exceptions import SemanticError

from mojo.results.model.taskinggroup import TaskingGroup
from mojo.results.model.taskingresult import TaskingResult

from mojo.interop.protocols.tasker.taskeraspects import TaskerAspects, DEFAULT_TASKER_ASPECTS
from mojo.interop.protocols.tasker.taskernode import TaskerNode
from mojo.interop.protocols.tasker.tasking import Tasking, TaskingIdentity
from mojo.interop.protocols.tasker.taskingresultpromise import TaskingResultPromise
from mojo.interop.protocols.tasker.taskercontroller import TaskerController


if TYPE_CHECKING:
    from mojo.interop.protocols.tasker.taskingadapter import TaskingAdapter


class TaskingGroupState:
    NotStarted = 0
    Running = 0
    Completed = 0


class TaskingGroupScope:
    """
    """

    def __init__(self, name: str, adapter: "TaskingAdapter", controller: TaskerController, tgroup: TaskingGroup, tnodes: List[TaskerNode],
                 aspects: TaskerAspects):

        self._name = name
        self._adapter_ref = weakref.ref(adapter)
        self._controller = controller
        self._tgroup = tgroup
        self._tnodes: List[TaskerNode] = tnodes
        self._aspects = aspects
        
        self._state = TaskingGroupState.NotStarted
        self._promises = []

        return
    
    @property
    def adapter(self):
        return self._adapter_ref()

    @property
    def promises(self):
        plist = [p for p in self._promises]
        return plist

    def __enter__(self) -> "TaskingGroupScope":
        return self

    def __exit__(self, ex_type, ex_inst, ex_tb) -> bool:

        self.synchronize()

        self.finalize()

        return


    def execute_tasking(self, *, tasking: Union[TaskingIdentity, Type[Tasking]], aspects: Optional[TaskerAspects] = None,
                        **kwargs) -> List[TaskingResultPromise]:

        if self._state != TaskingGroupState.NotStarted:
            errmsg = f"The tasking group '{self._name}' has already been started."
            raise SemanticError(errmsg)

        adapter = self.adapter
        parent_id = self._tgroup.inst_id

        self._promises = self._controller.execute_tasking_on_node_list(self._tnodes, tasking=tasking, parent_id=parent_id,
                                                                       aspects=aspects, **kwargs)

        return self._promises


    def finalize(self):

        adapter = self.adapter

        adapter.checkin_tasker_nodes(self._tnodes)

        return


    def synchronize(self):

        adapter = self.adapter

        if len(self._promises) > 0:
            self.wait_for_tasking_results()

        return


    def wait_for_tasking_results(self, aspects: Optional[TaskerAspects] = None) -> List[TaskingResult]:
        
        adapter = self.adapter

        results = self._controller.wait_for_tasking_results(self._promises)

        return results