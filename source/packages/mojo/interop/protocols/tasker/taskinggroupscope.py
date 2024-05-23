from typing import Dict, List, Optional, Type, Union, TYPE_CHECKING

import logging
import os
import weakref

from mojo.errors.exceptions import SemanticError
from mojo.errors.xtraceback import format_exception

from mojo.results.model.taskinggroup import TaskingGroup
from mojo.results.model.taskingresult import TaskingResult
from mojo.results.model.progressinfo import ProgressInfo
from mojo.results.model.progressdelivery import ProgressDeliveryMethod, SummaryProgressDelivery

from mojo.results.recorders.resultrecorder import ResultRecorder

from mojo.interop.protocols.tasker.taskeraspects import TaskerAspects

from mojo.interop.protocols.tasker.taskernode import TaskerNode
from mojo.interop.protocols.tasker.tasking import Tasking, TaskingIdentity
from mojo.interop.protocols.tasker.taskingresultpromise import TaskingResultPromise
from mojo.interop.protocols.tasker.taskercontroller import TaskerController
from mojo.interop.protocols.tasker.taskingevent import TaskingEvent

if TYPE_CHECKING:
    from mojo.testplus.sequencing.testsequencer import TestSequencer
    from mojo.interop.protocols.tasker.taskingadapter import TaskingAdapter


logger = logging.getLogger()


class TaskingGroupState:
    NotStarted = 0
    Running = 0
    Completed = 0


class TaskingGroupScope:
    """
    """

    def __init__(self, name: str, adapter: "TaskingAdapter", controller: TaskerController,
                 recorder: ResultRecorder, tgroup: TaskingGroup, tnodes: List[TaskerNode],
                 aspects: TaskerAspects, sequencer: Optional["TestSequencer"]=None):

        self._name = name
        self._adapter_ref = weakref.ref(adapter)
        self._controller = controller
        self._recorder = recorder
        self._tgroup = tgroup
        self._tnodes: List[TaskerNode] = tnodes
        self._aspects = aspects
        self._sequencer = sequencer
        
        self._state = TaskingGroupState.NotStarted
        self._promises: List[TaskingResultPromise] = []
        self._results = None
        self._results_written  = False

        self._progress_reported = False

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

    @property
    def sequencer(self) -> "TestSequencer":
        return self._sequencer
    
    @property
    def nodes(self) -> List[TaskerNode]:
        return self._tnodes

    def __enter__(self) -> "TaskingGroupScope":
        self.initialize()
        return self


    def __exit__(self, ex_type, ex_inst, ex_tb) -> bool:

        if ex_inst is not None:
            err_msg = format_exception(ex_inst)
            logger.error(err_msg)

            self.cancel_tasks()

        # We don't want to handle exceptions here,  If any AssertionError types come through, they
        # are likely due to a consolidated check, and they should be allowed to propagate.

        if self._progress_reported:
            self._clear_summary_progress()

        self.finalize()
        return False

    def initialize(self):
        self._recorder.record(self._tgroup)
        return

    def cancel_tasks(self):

        errors = []

        for promise in self._promises:
            try:
                promise.cancel()
            except Exception as xcpt:
                errors.append((promise.tasking_id, xcpt))

        if len(errors) > 0:
            errmsg_lines = [
                "Errors encountered while attempting to cancel tasks.",
                "ERRORS:"
            ]

            xcpt: Exception
            for tasking_id, xcpt in errors:
                message = str(xcpt)
                errmsg_lines.append(f"    {tasking_id}: {message}")

            err_msg = os.linesep.join(errmsg_lines)
            raise RuntimeError(err_msg)

        return

    def execute_tasking(self, *, tasking: Union[TaskingIdentity, Type[Tasking]], ncount: int = 1, aspects: Optional[TaskerAspects] = None,
                        **kwargs) -> List[TaskingResultPromise]:

        if aspects is None:
            aspects = self._aspects

        if self._state != TaskingGroupState.NotStarted:
            errmsg = f"The tasking group '{self._name}' has already been started."
            raise SemanticError(errmsg)

        adapter = self.adapter
        parent_id = self._tgroup.inst_id

        new_promises = self._controller.execute_tasking_on_node_list(
                self._tnodes, tasking=tasking, ncount=ncount, parent_id=parent_id, aspects=aspects, **kwargs)
        self._promises.extend(new_promises)

        return new_promises

    def execute_tasking_on_node(self, node: TaskerNode, *, tasking: Union[TaskingIdentity, Type[Tasking]], ncount: int = 1, aspects: Optional[TaskerAspects] = None,
                        **kwargs) -> List[TaskingResultPromise]:

        if aspects is None:
            aspects = self._aspects

        if self._state != TaskingGroupState.NotStarted:
            errmsg = f"The tasking group '{self._name}' has already been started."
            raise SemanticError(errmsg)

        adapter = self.adapter
        parent_id = self._tgroup.inst_id

        promise = self._controller.execute_tasking_on_node(
                node, tasking=tasking, ncount=ncount, parent_id=parent_id, aspects=aspects, **kwargs)
        self._promises.append(promise)

        return promise

    def finalize(self, sync: bool = True):

        adapter = self.adapter

        if sync:
            self.synchronize()

        self._tgroup.finalize()
        self._recorder.record(self._tgroup)

        adapter.checkin_tasker_nodes(self._tnodes)

        return

    def mark_activity(self, activity_name: str, target: str="NA", detail: Optional[dict] = None):
        """
            A convenience method for marking activity in the current test scope.
        """
        if self._sequencer is not None:
            self._sequencer.mark_activity(activity_name, target=target, detail=detail)
        return

    def synchronize(self):

        adapter = self.adapter

        if len(self._promises) > 0:
            self.wait_for_tasking_results()

        return


    def wait_for_all_to_event(self, event_name: str, aspects: Optional[TaskerAspects] = None) -> List[TaskingEvent]:

        if aspects is None:
            aspects = self._aspects

        events_found = self._controller.wait_for_all_to_event(event_name, self._promises)

        return events_found

    def wait_for_any_to_event(self, event_name: str, aspects: Optional[TaskerAspects] = None) -> List[TaskingEvent]:

        if aspects is None:
            aspects = self._aspects

        events_found = self._controller.wait_for_any_to_event(event_name, self._promises)

        return events_found

    def wait_for_tasking_results(self, aspects: Optional[TaskerAspects] = None) -> List[TaskingResult]:

        if aspects is None:
            aspects = self._aspects

        if self._results is None:
            self._results = self._controller.wait_for_tasking_results(self._promises, aspects=aspects)
            self._update_group()

        return self._results
    

    def _clear_summary_progress(self):

        task_ids = []
    
        # Collect the progress
        for p in self._promises:
            task_ids.append(p.tasking_id)

        self._recorder.clear_task_progress(task_ids)
        self._recorder.update_summary()

        return


    def _notify_summary_progress(self, progress_list: List[ProgressInfo]):
        self._progress_reported = True

        self._recorder.post_task_progress(progress_list)
        self._recorder.update_summary()

        return


    def _update_group(self):

        if not self._results_written:
            self._results_written = True
            for res in self._results:
                self._recorder.record(res)

        return
