
from typing import Protocol


from mojo.results.recorders.resultrecorder import ResultRecorder
from mojo.results.model.taskinggroup import TaskingGroup
from mojo.results.model.taskingresult import TaskingResult


class ITaskingSequencer(Protocol):

    def create_tasking_result(self, scope_id: str, name: str, parent_inst: str) -> TaskingResult:
        """
            Method for creating a tasking result that is used to record tasking results in
            a test framework.
        """
    
    def create_tasking_group(self, scope_id: str, name: str, parent_inst: str) -> TaskingGroup:
        """
            Method for creating a tasking result group that is used for grouping tasking
            results by a test framework.
        """

    def get_recorder(self) -> ResultRecorder:
        """
            Method to get the 'ResultRecorder' recorder for a job run from the sequencer.
        """

    def get_top_scope_id(self) -> str:
        """
            Gets the scope id that is on top of the scope stack.
        """
