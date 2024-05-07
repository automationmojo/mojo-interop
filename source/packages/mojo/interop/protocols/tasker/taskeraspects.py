"""
.. module:: taskeraspects
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`TaskerAspects` class which is used to instruct behavior
    around tasking.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>

"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []



from typing import Dict, Optional 


DEFAULT_COMPLETION_TIMEOUT = 7 * 24 * 60 * 60   # The Default Timeout is 1 Week
DEFAULT_COMPLETION_INTERVAL = 10

DEFAULT_INACTIVITY_TIMEOUT = 1200 # 20 Minutes
DEFAULT_INACTIVITY_INTERVAL = .5

DEFAULT_PROGRESS_INTERVAL = 30

from mojo.results.model.progressdelivery import ProgressDeliveryMethod

class TaskerAspects:

    def __init__(self, completion_timeout: Optional[float] = DEFAULT_COMPLETION_TIMEOUT,
                       completion_interval: Optional[float] = DEFAULT_COMPLETION_INTERVAL,
                       inactivity_timeout: Optional[float] = DEFAULT_INACTIVITY_TIMEOUT,
                       inactivity_interval: Optional[float] = DEFAULT_INACTIVITY_INTERVAL,
                       progress_delivery: Optional[Dict[str, float]]= None,
                       sync_request_timeout: Optional[float]=None):
        
        self.completion_timeout = completion_timeout
        self.completion_interval = completion_interval
        self.inactivity_timeout = inactivity_timeout
        self.inactivity_interval = inactivity_interval
        self.progress_delivery = progress_delivery
        self.sync_request_timeout = sync_request_timeout
        return

    def as_dict(self) -> dict:
        data = {
            "completion_timeout": self.completion_timeout,
            "completion_interval": self.completion_interval,
            "inactivity_timeout": self.inactivity_timeout,
            "inactivity_interval": self.inactivity_interval,
            "progress_delivery": self.progress_delivery,
            "sync_request_timeout": self.sync_request_timeout
        }
        return data
    
    @classmethod
    def from_dict(self, data: dict) -> "TaskerAspects":
        obj = TaskerAspects(**data)
        return obj


DEFAULT_TASKER_ASPECTS = TaskerAspects()

DEFAULT_SUMMARY_PROGRESS_TASKER_ASPECTS = TaskerAspects(
    progress_delivery={ ProgressDeliveryMethod.SUMMARY_PULL_PROGRESS: DEFAULT_PROGRESS_INTERVAL }
)
