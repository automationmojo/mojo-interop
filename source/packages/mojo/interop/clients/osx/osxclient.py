"""
.. module:: osxclient
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the OsxClient object.

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

from typing import TYPE_CHECKING

from mojo.xmods.landscaping.friendlyidentifier import FriendlyIdentifier
from mojo.xmods.landscaping.client.clientbase import ClientBase

from mojo.interop.protocols.ssh.sshagent import SshAgent

if TYPE_CHECKING:
    from mojo.xmods.landscaping.landscape import Landscape
    from mojo.xmods.landscaping.coordinators.coordinatorbase import CoordinatorBase

class OsxClient(ClientBase):

    def __init__(self, lscape: "Landscape", coordinator: "CoordinatorBase",
                 friendly_id:FriendlyIdentifier, device_type: str, device_config: dict):
        super().__init__(lscape, coordinator, friendly_id, device_type, device_config)
        return

    @property
    def ssh(self) -> SshAgent:
        sshagent = self._extensions["network/ssh"]
        return sshagent