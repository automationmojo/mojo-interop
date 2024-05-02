"""
.. module:: mojointeroplandscapingfactories
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module that contains the factories for extending the Landscaping package to
               support included interop protocols.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []


from typing import List, Type

from mojo.extension.extensionfactory import ExtFactory

from mojo.xmods.injection.coupling.integrationcoupling import IntegrationCoupling

from mojo.landscaping.landscapingextensionprotocol import LandscapingExtensionProtocol

from mojo.interop.clients.linux.linuxclientcoordinatorcoupling import LinuxClientCoordinatorCoupling
from mojo.interop.clients.osx.osxclientcoordinatorcoupling import OsxClientCoordinatorCoupling
from mojo.interop.clients.windows.windowsclientcoordinatorcoupling import WindowsClientCoordinatorCoupling

from mojo.interop.protocols.serial.tcpserialcoordinatorcoupling import TcpSerialCoordinatorCoupling
from mojo.interop.protocols.ssh.sshcoordinatorcoupling import SshCoordinatorCoupling
from mojo.interop.protocols.power.dlipower.dlipowercoordinatorcoupling import PowerCoordinatorCoupling

from mojo.interop.services.vmware.vsphere.vspherecoordinatorcoupling import VSphereCoordinatorCoupling

class MojoInteropLandscapingExtentionFactory(ExtFactory, LandscapingExtensionProtocol):

    PRECEDENCE = 10

    @classmethod
    def get_landscape_type(self) -> Type:
        from mojo.landscaping.landscape import Landscape
        return Landscape
    
    @classmethod
    def get_integration_coupling_types(self) -> List[Type[IntegrationCoupling]]:
        """
            Used to lookup and return the most relevant list of integration coupling types.
        """
        coupling_types = [
            LinuxClientCoordinatorCoupling,
            OsxClientCoordinatorCoupling,
            PowerCoordinatorCoupling,
            SshCoordinatorCoupling,
            TcpSerialCoordinatorCoupling,
            VSphereCoordinatorCoupling,
            WindowsClientCoordinatorCoupling
        ]
        return coupling_types
