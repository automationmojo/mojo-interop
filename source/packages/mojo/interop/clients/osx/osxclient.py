"""
.. module:: osxclient
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the OsxClient object.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []



from typing import TYPE_CHECKING

from mojo.interfaces.isystemcontext import ISystemContext
from mojo.landscaping.friendlyidentifier import FriendlyIdentifier
from mojo.landscaping.client.clientbase import ClientBase

from mojo.interop.protocols.ssh.sshagent import SshAgent

if TYPE_CHECKING:
    from mojo.landscaping.landscape import Landscape
    from mojo.landscaping.coordinators.coordinatorbase import CoordinatorBase

class OsxClient(ClientBase):

    def __init__(self, lscape: "Landscape", coordinator: "CoordinatorBase",
                 friendly_id:FriendlyIdentifier, device_type: str, device_config: dict):
        super().__init__(lscape, coordinator, friendly_id, device_type, device_config)
        return

    @property
    def ssh(self) -> SshAgent:
        sshagent = self._extensions["network/ssh"]
        return sshagent
    
    def get_default_system_context(self) -> ISystemContext:
        """
            Called to get an ISystemContext instance that is a default system type.
        """
        return self.ssh