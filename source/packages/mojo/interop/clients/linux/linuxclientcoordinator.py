"""
.. module:: linuxclientcoordinator
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the LinuxPoolCoordinator which is used for managing connectivity with pools of LINUX capable devices

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []


from typing import Any, Dict, Optional, TYPE_CHECKING

from mojo.errors.exceptions import NotOverloadedError

from mojo.credentials.basecredential import BaseCredential
from mojo.landscaping.client.clientcoordinatorbase import ClientCoordinatorBase

from mojo.interop.clients.constants import INTEGRATION_CLASS_FOR_LINUX_CLIENT
from mojo.interop.clients.linux.linuxclient import LinuxClient

from mojo.interop.protocols.ssh.sshagent import SshAgent
from mojo.interop.protocols.ssh.sshcoordinator import SUPPORTED_INTEGRATION_CLASS

if TYPE_CHECKING:
    from mojo.landscaping.landscape import Landscape

class LinuxClientCoordinator(ClientCoordinatorBase):
    """
        The :class:`LinuxPoolCoordinator` creates a pool of agents that can be used to
        coordinate the interop activities of the automation process and remote Linux
        client.
    """

    INTEGRATION_CLASS = INTEGRATION_CLASS_FOR_LINUX_CLIENT
    CLIENT_TYPE = LinuxClient

    # pylint: disable=attribute-defined-outside-init

    def __init__(self, lscape: "Landscape", *args, **kwargs):
        super().__init__(lscape, *args, **kwargs)
        return

    def create_ssh_agent(self, device: LinuxClient, device_info: Dict[str, Any], host: str, cred: BaseCredential,
                         users: Optional[dict] = None, port: int = 22, pty_params: Optional[dict] = None):
        
        ssh_agent = SshAgent(host, cred, users=users, port=port, pty_params=pty_params)

        device.attach_extension(SUPPORTED_INTEGRATION_CLASS, ssh_agent)
        return