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

DEFAULT_TASKER_ASPECTS = TaskerAspects()