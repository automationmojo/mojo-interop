
from typing import List, Type

from mojo.xmods.extension.configured import ExtensionPointsFactory

from mojo.xmods.landscaping.coupling.integrationcoupling import IntegrationCoupling
from mojo.xmods.landscaping.extensionpoints import LandscapingExtentionPoints

from mojo.interop.clients.linux.linuxclientcoordinatorcoupling import LinuxClientCoordinatorCoupling
from mojo.interop.clients.osx.osxclientcoordinatorcoupling import OsxClientCoordinatorCoupling
from mojo.interop.clients.windows.windowsclientcoordinatorcoupling import WindowsClientCoordinatorCoupling

from mojo.interop.protocols.serial.tcpserialcoordinatorcoupling import TcpSerialCoordinatorCoupling
from mojo.interop.protocols.ssh.sshcoordinatorcoupling import SshCoordinatorCoupling
from mojo.interop.protocols.power.dlipower.dlipowercoordinatorcoupling import PowerCoordinatorCoupling

from mojo.interop.services.vmware.vsphere.vspherecoordinatorcoupling import VSphereCoordinatorCoupling

class LandscapingExtentionPointsFactory(ExtensionPointsFactory, LandscapingExtentionPoints):

    @classmethod
    def get_landscape_type(self) -> Type:
        from mojo.xmods.landscaping.landscape import Landscape
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
