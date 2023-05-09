"""
.. module:: osxclientcoordinator
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the OsxPoolCoordinator which is used for managing connectivity with pools of OSX capable devices

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

from typing import Any, Dict, Optional, TYPE_CHECKING

from mojo.xmods.credentials.basecredential import BaseCredential
from mojo.xmods.landscaping.client.clientcoordinatorbase import ClientCoordinatorBase

from mojo.interop.clients.constants import INTEGRATION_CLASS_FOR_OSX_CLIENT
from mojo.interop.clients.osx.osxclient import OsxClient

from mojo.interop.protocols.ssh.sshagent import SshAgent
from mojo.interop.protocols.ssh.sshcoordinator import SUPPORTED_INTEGRATION_CLASS

if TYPE_CHECKING:
    from mojo.xmods.landscaping.landscape import Landscape

class OsxClientCoordinator(ClientCoordinatorBase):
    """
        The :class:`OsxPoolCoordinator` creates a pool of agents that can be used to
        coordinate the interop activities of the automation process and remote OSX
        client.
    """

    INTEGRATION_CLASS = INTEGRATION_CLASS_FOR_OSX_CLIENT
    CLIENT_TYPE = OsxClient

    # pylint: disable=attribute-defined-outside-init

    def __init__(self, lscape: "Landscape", *args, **kwargs):
        super().__init__(lscape, *args, **kwargs)
        return

    def create_ssh_agent(self, device: OsxClient, device_info: Dict[str, Any], host: str, cred: BaseCredential,
                         users: Optional[dict] = None, port: int = 22, pty_params: Optional[dict] = None):
        
        ssh_agent = SshAgent(host, cred, users=users, port=port, pty_params=pty_params)

        device.attach_extension(SUPPORTED_INTEGRATION_CLASS, ssh_agent)
        return