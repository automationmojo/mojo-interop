"""
.. module:: tcpserialdevice
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the TcpSerialDevice object.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []



from typing import TYPE_CHECKING

from mojo.landscaping.landscapedevice import LandscapeDevice
from mojo.landscaping.friendlyidentifier import FriendlyIdentifier

from mojo.interop.protocols.serial.tcpserialagent import TcpSerialAgent

if TYPE_CHECKING:
    from mojo.landscaping.landscape import Landscape
    from mojo.landscaping.coordinators.coordinatorbase import CoordinatorBase

class TcpSerialDevice(LandscapeDevice):

    def __init__(self, lscape: "Landscape", coordinator: "CoordinatorBase",
                 friendly_id:FriendlyIdentifier, device_type: str, device_config: dict):
        super().__init__(lscape, coordinator, friendly_id, device_type, device_config)

        self._host = device_config["host"]
        self._port = device_config["port"]
        return

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    @property
    def serial(self) -> TcpSerialAgent:
        ext = self._extensions["network/ssh"]
        return ext

    def enhance(self):
        """
            Called to allow a device to enhance its metadata past what is declared in the
            configuration file.  For device that only have a hint, this might trigger a
            discovery process which will result in determining connectivity with the device.
        """
        return
