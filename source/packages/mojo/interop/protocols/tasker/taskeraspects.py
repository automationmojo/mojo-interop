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
__version__ = "1.0.0"
__maintainer__ = "Myron Walker"
__email__ = "myron.walker@gmail.com"
__status__ = "Development" # Prototype, Development or Production
__license__ = "MIT"


from typing import Dict, Optional 


DEFAULT_COMPLETION_TIMEOUT = 7 * 24 * 60 * 60   # The Default Timeout is 1 Week
DEFAULT_COMPLETION_INTERVAL = 10

DEFAULT_INACTIVITY_TIMEOUT = 600
DEFAULT_INACTIVITY_INTERVAL = .5

DEFAULT_PROGRESS_INTERVAL = 30

from mojo.results.model.progressdelivery import ProgressDeliveryMethod

class TaskerAspects:

    def __init__(self, completion_timeout: Optional[float] = DEFAULT_COMPLETION_TIMEOUT,
                       completion_interval: Optional[float] = DEFAULT_COMPLETION_INTERVAL,
                       inactivity_timeout: Optional[float] = DEFAULT_INACTIVITY_TIMEOUT,
                       inactivity_interval: Optional[float] = DEFAULT_INACTIVITY_INTERVAL,
                       progress_delivery: Optional[Dict[str, float]]= None):
        
        self.completion_timeout = completion_timeout
        self.completion_interval = completion_interval
        self.inactivity_timeout = inactivity_timeout
        self.inactivity_interval = inactivity_interval
        self.progress_delivery = progress_delivery
        return

DEFAULT_TASKER_ASPECTS = TaskerAspects()

DEFAULT_SUMMARY_PROGRESS_TASKER_ASPECTS = TaskerAspects(
    progress_delivery={ ProgressDeliveryMethod.SUMMARY_PULL_PROGRESS: DEFAULT_PROGRESS_INTERVAL }
)
