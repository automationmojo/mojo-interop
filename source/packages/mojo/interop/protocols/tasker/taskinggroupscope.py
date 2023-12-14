from typing import List, Optional, Type, Union, TYPE_CHECKING

import logging
import weakref

from mojo.errors.exceptions import SemanticError

from mojo.results.model.taskinggroup import TaskingGroup
from mojo.results.model.taskingresult import TaskingResult
from mojo.results.recorders.resultrecorder import ResultRecorder

from mojo.interop.protocols.tasker.taskeraspects import TaskerAspects, DEFAULT_TASKER_ASPECTS
from mojo.interop.protocols.tasker.taskernode import TaskerNode
from mojo.interop.protocols.tasker.tasking import Tasking, TaskingIdentity
from mojo.interop.protocols.tasker.taskingresultpromise import TaskingResultPromise
from mojo.interop.protocols.tasker.taskercontroller import TaskerController


if TYPE_CHECKING:
    from mojo.interop.protocols.tasker.taskingadapter import TaskingAdapter


logger = logging.getLogger()


class TaskingGroupState:
    NotStarted = 0
    Running = 0
    Completed = 0


class TaskingGroupScope:
    """
    """

    def __init__(self, name: str, adapter: "TaskingAdapter", controller: TaskerController, recorder: ResultRecorder, tgroup: TaskingGroup, tnodes: List[TaskerNode],
                 aspects: TaskerAspects):

        self._name = name
        self._adapter_ref = weakref.ref(adapter)
        self._controller = controller
        self._recorder = recorder
        self._tgroup = tgroup
        self._tnodes: List[TaskerNode] = tnodes
        self._aspects = aspects
        
        self._state = TaskingGroupState.NotStarted
        self._promises = []
        self._results = None
        self._results_written  = False

        return


    @property
    def adapter(self) -> "TaskingAdapter":
        return self._adapter_ref()


    @property
    def name(self) -> str:
        return self._name


    @property
    def promises(self) -> List[TaskingResultPromise]:
        plist = [p for p in self._promises]
        return plist


    def __enter__(self) -> "TaskingGroupScope":
        self.initialize()
        return self


    def __exit__(self, ex_type, ex_inst, ex_tb) -> bool:

        # We don't want to handle exceptions here,  If any AssertionError types come through, they
        # are likely due to a consolidated check, and they should be allowed to propagate.

        self.finalize()

        return False

    def initialize(self):
        self._recorder.record(self._tgroup)
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


    def finalize(self, sync: bool = True):

        adapter = self.adapter

        if sync:
            self.synchronize()

        self._tgroup.finalize()
        self._recorder.record(self._tgroup)

        adapter.checkin_tasker_nodes(self._tnodes)

        return


    def synchronize(self):

        adapter = self.adapter

        if len(self._promises) > 0:
            self.wait_for_tasking_results()

        return


    def wait_for_tasking_results(self, aspects: Optional[TaskerAspects] = None) -> List[TaskingResult]:

        if self._results is None:
            adapter = self.adapter

            self._results = self._controller.wait_for_tasking_results(self._promises)
            self._update_group()

        return self._results
    
    def _update_group(self):

        if not self._results_written:
            self._results_written = True
            for res in self._results:
                self._recorder.record(res)

        return
