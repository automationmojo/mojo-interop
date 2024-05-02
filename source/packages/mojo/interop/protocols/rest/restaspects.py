
__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []


from typing import List, Optional, Union

import logging

from enum import IntEnum

from requests import Session

from mojo.xmods.aspects import (
    Aspects,
    ActionPattern,
    LoggingPattern,
    DEFAULT_COMPLETION_TIMEOUT,
    DEFAULT_COMPLETION_INTERVAL,
    DEFAULT_CONNECTION_TIMEOUT,
    DEFAULT_CONNECTION_INTERVAL,
    DEFAULT_INACTIVITY_TIMEOUT,
    DEFAULT_INACTIVITY_INTERVAL,
    DEFAULT_MONITOR_DELAY,
    DEFAULT_LOGGING_PATTERN,
    DEFAULT_RETRY_LOGGING_INTERVAL,
    DEFAULT_ALLOWED_ERROR_CODES,
    DEFAULT_ALLOWED_CONNECTION_EXCEPTIONS,
    DEFAULT_MUST_CONNECT
)

class RestAspects(Aspects):
    """
    """
    def __init__(self, *, action_pattern: ActionPattern = ActionPattern.SINGLE_CALL,
                completion_timeout: float = DEFAULT_COMPLETION_TIMEOUT,
                completion_interval: float = DEFAULT_COMPLETION_INTERVAL,
                connection_timeout: float = DEFAULT_CONNECTION_TIMEOUT,
                connection_interval: float = DEFAULT_CONNECTION_INTERVAL,
                inactivity_timeout: float = DEFAULT_INACTIVITY_TIMEOUT,
                inactivity_interval: float = DEFAULT_INACTIVITY_INTERVAL,
                monitor_delay: float = DEFAULT_MONITOR_DELAY,
                logging_pattern: LoggingPattern = DEFAULT_LOGGING_PATTERN,
                retry_logging_interval: int = DEFAULT_RETRY_LOGGING_INTERVAL,
                allowed_error_codes: List[int] = DEFAULT_ALLOWED_ERROR_CODES,
                allowed_connection_exceptions: List[BaseException] = DEFAULT_ALLOWED_CONNECTION_EXCEPTIONS,
                must_connect: bool = DEFAULT_MUST_CONNECT,
                logger: Optional[logging.Logger]=None,
                session: Optional[Session] = None):
        super().__init__(action_pattern=action_pattern, completion_timeout=completion_timeout,
                         completion_interval=completion_interval, connection_timeout=connection_timeout,
                         connection_interval=connection_interval, inactivity_timeout=inactivity_timeout,
                         inactivity_interval=inactivity_interval, monitor_delay=monitor_delay,
                         logging_pattern=logging_pattern, retry_logging_interval=retry_logging_interval,
                         allowed_error_codes=allowed_error_codes, allowed_connection_exceptions=allowed_connection_exceptions,
                         must_connect=must_connect, logger=logger)
        self._session = session
        return
    
    @property
    def session(self) -> Union[Session, None]:
        return self._session



DEFAULT_REST_ASPECTS = RestAspects()

