
from typing import Generator

from mojo import testplus

from mojo.landscaping.wellknown import LandscapeSingleton
from mojo.landscaping.landscape import Landscape

from mojo.interop.clients.linux.linuxclientcoordinatorcoupling import LinuxClientCoordinatorCoupling

@testplus.resource()
def create_landscape(constraints={}) -> Generator[Landscape, None, None]:
    lscape = LandscapeSingleton()
    yield lscape

@testplus.integration()
def create_linux_client_coordinator_coupling() -> Generator[LinuxClientCoordinatorCoupling, None, None]:
    lc_coupling = LinuxClientCoordinatorCoupling()
    yield lc_coupling
