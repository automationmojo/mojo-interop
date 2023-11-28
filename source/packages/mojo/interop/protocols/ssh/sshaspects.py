
from mojo.xmods.aspects import (
    AspectsCmd,
    DEFAULT_CMD_ASPECTS
)

from paramiko.ssh_exception import (
    AuthenticationException,
    NoValidConnectionsError,
    BadAuthenticationType
)

DEFAULT_SSH_ASPECTS = DEFAULT_CMD_ASPECTS

UNDER_CONSTRUCTION_SSH_ALLOWED_EXCEPTIONS = [NoValidConnectionsError, BadAuthenticationType, AuthenticationException]
UNDER_CONSTRUCTION_SSH_CONNECTION_TIMEOUT = 60
UNDER_CONSTRUCTION_SSH_CONNECTION_INTERVAL = 5

UNDER_CONSTRUCTION_SSH_ASPECTS = AspectsCmd(
    connection_timeout=UNDER_CONSTRUCTION_SSH_CONNECTION_TIMEOUT,
    connection_interval=UNDER_CONSTRUCTION_SSH_CONNECTION_INTERVAL,
    allowed_connection_exceptions=UNDER_CONSTRUCTION_SSH_ALLOWED_EXCEPTIONS
)