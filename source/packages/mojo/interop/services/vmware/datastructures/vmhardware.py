"""
.. module:: vmhardware
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains various VmHardware*Spec related objects used in the creation of VM(s).

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

from typing import Optional

from mojo.interop.services.vmware.metasphere.vmhardware import (
    VmHardwareBootNetworkProtocol,
    VmHardwareBootType
)

from dataclasses import dataclass

class VmHardwareCpuUpdateSpec(dataclass):
    cores_per_socket: Optional[int] = None
    count: Optional[int] = None
    hot_add_enabled: Optional[bool] = None
    hot_remove_enabled: Optional[bool] = None

class VmHardwareBootCreateSpec(dataclass):
    delay: Optional[int] = None
    efi_lagacy_boot: Optional[bool] = None
    enter_setup_mode: Optional[bool] = None
    network_protocol: Optional[VmHardwareBootNetworkProtocol] = None
    retry: Optional[bool] = None
    retry_delay: Optional[int] = None
    boot_type: Optional[VmHardwareBootType] = None

class VmHardwareMemoryUpdateSpec(dataclass):
    hot_add_enabled: Optional[bool] = None
    size_MiB: Optional[int] = None
