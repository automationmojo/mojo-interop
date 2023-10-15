
from typing import Optional 

DEFAULT_COMPLETION_TIMEOUT = 600
DEFAULT_COMPLETION_INTERVAL = 10

DEFAULT_INACTIVITY_TIMEOUT = 600
DEFAULT_INACTIVITY_INTERVAL = .5

class TaskerAspects:

    def __init__(self, completion_timeout: Optional[float] = None,
                       completion_interval: Optional[float] = DEFAULT_COMPLETION_INTERVAL,
                       inactivity_timeout: Optional[float] = None,
                       inactivity_interval: Optional[float] = DEFAULT_INACTIVITY_INTERVAL):
        
        self.completion_timeout = completion_timeout
        self.completion_interval = completion_interval
        self.inactivity_timeout = inactivity_timeout
        self.inactivity_interval = inactivity_interval
        return
