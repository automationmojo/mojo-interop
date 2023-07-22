"""
.. module:: vmhardware
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains various VmHardware*Spec related objects used in the creation of VM(s).

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

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
    delay: Optional[int]
    efi_lagacy_boot: Optional[bool]
    enter_setup_mode: Optional[bool]
    network_protocol: Optional[VmHardwareBootNetworkProtocol]
    retry: Optional[bool]
    retry_delay: Optional[int]
    boot_type: Optional[bool]

@dataclass
class VmHardwareCpuUpdateSpec:
    cores_per_socket: Optional[int]
    count: Optional[int]
    hot_add_enabled: Optional[bool]
    hot_remove_enabled: Optional[bool]

@dataclass
class VmHardwareDiskBackingSpec:
    backing_type: Optional[VmHardwareDiskBackingType]
    vmdk_file: Optional[str]

@dataclass
class VmHardwareIdeAddressSpec:
    master: Optional[bool]
    primary: Optional[bool]

@dataclass
class VmHardwareDiskStoragePolicySpec:
    policy: str

@dataclass
class VmHardwareDiskVmdkCreateSpec:
    capacity: Optional[int]
    name: Optional[str]
    storage_policy: Optional[VmHardwareDiskStoragePolicySpec]

@dataclass
class VmHardwareNvmeAddressSpec:
    bus: int
    unit: Optional[int]

@dataclass
class VmHardwareSataAddressSpec:
    bus: int
    unit: Optional[int]

@dataclass
class VmHardwareScsiAddressSpec:
    bus: int
    unit: Optional[int]

@dataclass
class VmHardwareDiskCreateSpec:
    backing: Optional[VmHardwareDiskBackingType]
    ide: Optional[VmHardwareIdeAddressSpec]
    new_vmdk: Optional[VmHardwareDiskVmdkCreateSpec]
    nvme: Optional[VmHardwareNvmeAddressSpec]
    sata: Optional[VmHardwareSataAddressSpec]
    scsi: Optional[VmHardwareScsiAddressSpec]
    type: Optional[VmHardwareDiskHostBusAdapterType]

@dataclass
class VmHardwareFloppyBackingSpec:
    host_device: Optional[str]
    image_file: Optional[str]
    type: VmHardwareFloppyBackingType

@dataclass
class VmHardwareFloppyCreateSpec:
    allow_guest_control: Optional[bool]
    backing: Optional[VmHardwareFloppyBackingSpec]
    start_connected: Optional[str]

@dataclass
class VmHardwareCdromBackingSpec:
    device_access_type: Optional[VmHardwareCdromDeviceAccessType]
    host_device: Optional[str]
    iso_file: Optional[str]
    type: Optional[VmHardwareCdromBackingType]

@dataclass
class VmHardwareCdromCreateSpec:
    allow_guest_control: Optional[str]
    backing: Optional[VmHardwareCdromBackingSpec]
    ide: Optional[VmHardwareIdeAddressSpec]
    sata: Optional[VmHardwareSataAddressSpec]
    start_connected: Optional[bool]
    type: Optional[VmHardwareCdromHostBusAdapterType]

@dataclass
class VmHardwareMemoryUpdateSpec:
    hot_add_enabled: Optional[bool]
    size_MiB: Optional[int]


@dataclass
class VmHardwareEthernetBackingSpec:
    distributed_port: Optional[str]
    network: Optional[str]
    type: VmHardwareEthernetBackingType

@dataclass
class VmHardwareEthernetCreateSpec:
    allow_guest_control: Optional[bool]
    backing: Optional[VmHardwareEthernetBackingSpec]
    mac_address: Optional[str]
    mac_type: Optional[VmHardwareEthernetMacAddressType]
    pci_slot_number: Optional[int]
    start_connected: Optional[bool]
    type: VmHardwareEthernetEmulationType
    upt_compatibility_enabled: Optional[bool]
    wake_on_lan_enabled: Optional[bool]

@dataclass
class VmHardwareAdapterNvmeCreateSpec:
    bus: Optional[int]
    pci_slot_number: Optional[int]

@dataclass
class VmHardwareParallelBackingSpec:
    file: Optional[str]
    host_device: Optional[str]
    type: VmHardwareParallelBackingType

@dataclass
class VmHardwareParallelCreateSpec:
    allow_guest_control: Optional[bool]
    backing: Optional[VmHardwareParallelBackingSpec]
    start_connected: Optional[bool]

@dataclass
class VmHardwareBootDeviceEntryCreateSpec:
    type: VmHardwareBootDeviceType

@dataclass
class VmHardwareAdapterSataCreateSpec:
    bus: Optional[int]
    pci_slot_number: Optional[int]
    type: VmHardwareAdapterSataType

@dataclass
class VmHardwareAdapterScsiCreateSpec:
    bus: Optional[int]
    pci_slot_number: Optional[int]
    sharing: Optional[VmHardwareAdapterScsiSharing]
    type: Optional[VmHardwareAdapterScsiType]


@dataclass
class VmHardwareSerialBackingSpec:
    file: Optional[str]
    host_device: Optional[str]
    network_location: Optional[str]
    no_rx_loss: Optional[bool]
    pipe: Optional[str]
    proxy: Optional[str]
    type: VmHardwareSerialBackingType

@dataclass
class VmHardwareSerialCreateSpec:
    allow_guest_control: Optional[bool]
    backing: VmHardwareSerialBackingSpec
    start_connected: Optional[bool]
    yield_on_poll: Optional[bool]
