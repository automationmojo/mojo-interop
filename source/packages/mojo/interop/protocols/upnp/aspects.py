"""
.. module:: aspects
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module that contains the :class:`Aspects` class and the constants used to provide aspect behaviors.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2020, Myron W Walker"
__credits__ = []


from typing import List, Optional

import logging

from mojo.xmods.aspects import (
    Aspects,
    ActionPattern,
    LoggingPattern,
    DEFAULT_ALLOWED_ERROR_CODES,
    DEFAULT_COMPLETION_INTERVAL,
    DEFAULT_COMPLETION_TIMEOUT,
    DEFAULT_INACTIVITY_INTERVAL,
    DEFAULT_INACTIVITY_TIMEOUT,
    DEFAULT_LOGGING_PATTERN,
    DEFAULT_MONITOR_DELAY,
    DEFAULT_MUST_CONNECT,
    DEFAULT_RETRY_LOGGING_INTERVAL
)

class AspectsUPnP(Aspects):
    """
    """
    def __init__(self, action_pattern: ActionPattern = ActionPattern.SINGLE_CONNECTED_CALL,
                       completion_timeout: float = DEFAULT_COMPLETION_TIMEOUT,
                       completion_interval: float = DEFAULT_COMPLETION_INTERVAL,
                       inactivity_timeout: float = DEFAULT_INACTIVITY_TIMEOUT,
                       inactivity_interval: float = DEFAULT_INACTIVITY_INTERVAL,
                       monitor_delay: float = DEFAULT_MONITOR_DELAY,
                       logging_pattern: LoggingPattern = DEFAULT_LOGGING_PATTERN,
                       retry_logging_interval: int = DEFAULT_RETRY_LOGGING_INTERVAL,
                       allowed_error_codes: List[int] = DEFAULT_ALLOWED_ERROR_CODES,
                       must_connect: bool = DEFAULT_MUST_CONNECT,
                       logger: Optional[logging.Logger]=None):
        
        Aspects.__init__(self, action_pattern=action_pattern, completion_timeout=completion_timeout,
                            completion_interval=completion_interval, inactivity_timeout=inactivity_timeout,
                            inactivity_interval=inactivity_interval, monitor_delay=monitor_delay,
                            logging_pattern=logging_pattern, retry_logging_interval=retry_logging_interval,
                            allowed_error_codes=allowed_error_codes, must_connect=must_connect, logger=logger)
        return


DEFAULT_UPNP_ASPECTS = AspectsUPnP()
