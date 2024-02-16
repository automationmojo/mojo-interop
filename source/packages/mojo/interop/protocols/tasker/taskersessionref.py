
from typing import Dict, Optional, Union

from mojo.errors.exceptions import SemanticError
from mojo.interop.protocols.tasker.taskingprogresscallback import TaskingProgressCallback

class TaskerSessionRef:

    def __init__(self, id: str, notify_interval: Optional[float],
                 notify_callback: Optional[TaskingProgressCallback] = None):
        self._id = id
        
        if notify_callback is not None or notify_interval is not None:
            if notify_callback is None or notify_interval is None:
                errmsg = "If any notify parameter is passed then both 'notify_interval' and 'notify_callback' must be passed."
                raise SemanticError(errmsg)

        self._notify_interval = notify_interval
        self._notify_callback = notify_callback
        return
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def notify_interval(self) -> Union[Dict[str, str], None]:
        return self._notify_interval
    
    @property
    def notify_callback(self) -> Union[Dict[str, str], None]:
        return self._notify_callback
