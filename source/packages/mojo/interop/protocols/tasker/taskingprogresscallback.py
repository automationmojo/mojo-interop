
from typing import Protocol

from mojo.results.model.progressinfo import ProgressInfo

class TaskingProgressCallback(Protocol):

    def __call__(self, progress: ProgressInfo) -> None: ...
