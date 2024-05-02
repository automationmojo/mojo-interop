"""
.. module:: vmhardware
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains various VmHardware*Spec related objects used in the creation of VM(s).

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []


from typing import Optional

from dataclasses import dataclass

from mojo.interop.services.vmware.metasphere.vmhardware import (
    VmHardwareBootNetworkProtocol,
    VmHardwareBootType,
    VmHardwareDiskBackingType,
    VmHardwareDiskHostBusAdapterType,
    VmHardwareFloppyBackingType,
    VmHardwareCdromDeviceAccessType,
    VmHardwareCdromBackingType,
    VmHardwareCdromHostBusAdapterType,
    VmHardwareEthernetBackingType,
    VmHardwareEthernetMacAddressType,
    VmHardwareEthernetEmulationType,
    VmHardwareParallelBackingType,
    VmHardwareBootDeviceType,
    VmHardwareAdapterSataType,
    VmHardwareAdapterScsiSharing,
    VmHardwareAdapterScsiType,
    VmHardwareSerialBackingType
)
@dataclass
class VmHardwareBootCreateSpec:
    delay: Optional[int] = None
    efi_lagacy_boot: Optional[bool] = None
    enter_setup_mode: Optional[bool] = None
    network_protocol: Optional[VmHardwareBootNetworkProtocol] = None
    retry: Optional[bool] = None
    retry_delay: Optional[int] = None
    boot_type: Optional[bool] = None

@dataclass
class VmHardwareCpuUpdateSpec:
    cores_per_socket: Optional[int] = None
    count: Optional[int] = None
    hot_add_enabled: Optional[bool] = None
    hot_remove_enabled: Optional[bool] = None

@dataclass
class VmHardwareDiskBackingSpec:
    backing_type: Optional[VmHardwareDiskBackingType] = None
    vmdk_file: Optional[str] = None

@dataclass
class VmHardwareIdeAddressSpec:
    master: Optional[bool] = None
    primary: Optional[bool] = None

@dataclass
class VmHardwareDiskStoragePolicySpec:
    policy: str

@dataclass
class VmHardwareDiskVmdkCreateSpec:
    capacity: Optional[int] = None
    name: Optional[str] = None
    storage_policy: Optional[VmHardwareDiskStoragePolicySpec] = None

@dataclass
class VmHardwareNvmeAddressSpec:
    bus: int
    unit: Optional[int] = None

@dataclass
class VmHardwareSataAddressSpec:
    bus: int
    unit: Optional[int] = None

@dataclass
class VmHardwareScsiAddressSpec:
    bus: int
    unit: Optional[int] = None

@dataclass
class VmHardwareDiskCreateSpec:
    backing: Optional[VmHardwareDiskBackingType] = None
    ide: Optional[VmHardwareIdeAddressSpec] = None
    new_vmdk: Optional[VmHardwareDiskVmdkCreateSpec] = None
    nvme: Optional[VmHardwareNvmeAddressSpec] = None
    sata: Optional[VmHardwareSataAddressSpec] = None
    scsi: Optional[VmHardwareScsiAddressSpec] = None
    type: Optional[VmHardwareDiskHostBusAdapterType] = None

@dataclass
class VmHardwareFloppyBackingSpec:
    type: VmHardwareFloppyBackingType
    host_device: Optional[str] = None
    image_file: Optional[str] = None

@dataclass
class VmHardwareFloppyCreateSpec:
    allow_guest_control: Optional[bool] = None
    backing: Optional[VmHardwareFloppyBackingSpec] = None
    start_connected: Optional[str] = None

@dataclass
class VmHardwareCdromBackingSpec:
    device_access_type: Optional[VmHardwareCdromDeviceAccessType] = None
    host_device: Optional[str] = None
    iso_file: Optional[str] = None
    type: Optional[VmHardwareCdromBackingType] = None

@dataclass
class VmHardwareCdromCreateSpec:
    allow_guest_control: Optional[str] = None
    backing: Optional[VmHardwareCdromBackingSpec] = None
    ide: Optional[VmHardwareIdeAddressSpec] = None
    sata: Optional[VmHardwareSataAddressSpec] = None
    start_connected: Optional[bool] = None
    type: Optional[VmHardwareCdromHostBusAdapterType] = None

@dataclass
class VmHardwareMemoryUpdateSpec:
    hot_add_enabled: Optional[bool] = None
    size_MiB: Optional[int] = None


@dataclass
class VmHardwareEthernetBackingSpec:
    type: VmHardwareEthernetBackingType
    distributed_port: Optional[str] = None
    network: Optional[str] = None

@dataclass
class VmHardwareEthernetCreateSpec:
    type: VmHardwareEthernetEmulationType
    allow_guest_control: Optional[bool] = None
    backing: Optional[VmHardwareEthernetBackingSpec] = None
    mac_address: Optional[str] = None
    mac_type: Optional[VmHardwareEthernetMacAddressType] = None
    pci_slot_number: Optional[int] = None
    start_connected: Optional[bool] = None
    upt_compatibility_enabled: Optional[bool] = None
    wake_on_lan_enabled: Optional[bool] = None

@dataclass
class VmHardwareAdapterNvmeCreateSpec:
    bus: Optional[int] = None
    pci_slot_number: Optional[int] = None

@dataclass
class VmHardwareParallelBackingSpec:
    type: VmHardwareParallelBackingType
    file: Optional[str] = None
    host_device: Optional[str] = None

@dataclass
class VmHardwareParallelCreateSpec:
    allow_guest_control: Optional[bool] = None
    backing: Optional[VmHardwareParallelBackingSpec] = None
    start_connected: Optional[bool] = None

@dataclass
class VmHardwareBootDeviceEntryCreateSpec:
    type: VmHardwareBootDeviceType

@dataclass
class VmHardwareAdapterSataCreateSpec:
    type: VmHardwareAdapterSataType
    bus: Optional[int] = None
    pci_slot_number: Optional[int] = None

@dataclass
class VmHardwareAdapterScsiCreateSpec:
    bus: Optional[int] = None
    pci_slot_number: Optional[int] = None
    sharing: Optional[VmHardwareAdapterScsiSharing] = None
    type: Optional[VmHardwareAdapterScsiType] = None


@dataclass
class VmHardwareSerialBackingSpec:
    type: VmHardwareSerialBackingType
    file: Optional[str] = None
    host_device: Optional[str] = None
    network_location: Optional[str] = None
    no_rx_loss: Optional[bool] = None
    pipe: Optional[str] = None
    proxy: Optional[str] = None

@dataclass
class VmHardwareSerialCreateSpec:
    backing: VmHardwareSerialBackingSpec
    allow_guest_control: Optional[bool] = None
    start_connected: Optional[bool] = None
    yield_on_poll: Optional[bool] = None
