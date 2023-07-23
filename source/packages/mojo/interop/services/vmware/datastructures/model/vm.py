
from typing import List, Optional

from dataclasses import dataclass, asdict

from mojo.interop.services.vmware.metasphere.vmguestos import VmGuestOS
from mojo.interop.services.vmware.metasphere.vmhardware import (
    VmHardwareConnectionState,
    VmHardwareSerialBackingType,
    VmHardwareBootDeviceType,
    VmHardwareCdromDeviceAccessType,
    VmHardwareCdromBackingType,
    VmHardwareCdromHostBusAdapterType,
    VmHardwareDiskBackingType,
    VmHardwareDiskHostBusAdapterType,
    VmHardwareFloppyBackingType,
    VmHardwareUpgradePolicy,
    VmHardwareUpgradeStatus,
    VmHardwareVersion,
    VmHardwareAdapterScsiSharing,
    VmHardwareAdapterScsiType,
    VmHardwareBootType,
    VmHardwareBootNetworkProtocol,
    VmHardwareEthernetBackingType,
    VmHardwareEthernetMacAddressType,
    VmHardwareEthernetEmulationType,
    VmHardwareAdapterSataType,
    VmHardwareParallelBackingType,
    VmPowerState
)

@dataclass
class VmHardwareSerialBackingInfo:
    type: VmHardwareSerialBackingType
    auto_detect: Optional[bool] = None
    file: Optional[str] = None
    host_device: Optional[str] = None
    network_location: Optional[str] = None
    no_rx_loss: Optional[str] = None
    pipe: Optional[str] = None
    proxy: Optional[str] = None
    

@dataclass
class VmHardwareSerialInfo:
    allow_guest_control: bool
    backing: VmHardwareSerialBackingInfo
    label: str
    start_connected: bool
    state: VmHardwareConnectionState
    yield_on_poll: bool

@dataclass
class VmHardwareBootDeviceEntry:
    type: VmHardwareBootDeviceType
    disks: List[str]
    nic: str


@dataclass
class VmHardwareCdromBackingInfo:
    auto_detect: bool
    device_access_type: VmHardwareCdromDeviceAccessType
    host_device: str
    iso_file: str
    type: VmHardwareCdromBackingType

@dataclass
class VmHardwareIdeAddressInfo:
    master: bool
    primary: bool

@dataclass
class VmHardwareNvmeAddressInfo:
    bus: int
    unit: int


@dataclass
class VmHardwareSataAddressInfo:
    bus: int
    unit: int

@dataclass
class VmHardwareScsiAddressInfo:
    bus: int
    unit: int

@dataclass
class VmHardwareCdromInfo:
    allow_guest_control: bool
    backing: VmHardwareCdromBackingInfo
    label: str
    start_connected: bool
    state: VmHardwareConnectionState
    type: VmHardwareCdromHostBusAdapterType
    ide: VmHardwareIdeAddressInfo
    sata: VmHardwareSataAddressInfo

@dataclass
class VmHardwareCpuInfo:
    cores_per_socket: int
    count: int
    hot_add_enabled: bool
    hot_remove_enabled: bool

@dataclass
class VmHardwareDiskBackingInfo:
    type: VmHardwareDiskBackingType
    vmdk_file: str

@dataclass
class VmHardwareDiskInfo:
    backing: VmHardwareDiskBackingInfo
    type: VmHardwareDiskHostBusAdapterType
    label: str
    ide: Optional[VmHardwareIdeAddressInfo] = None
    nvme: Optional[VmHardwareNvmeAddressInfo] = None
    sata: Optional[VmHardwareSataAddressInfo] = None
    scsi: Optional[VmHardwareScsiAddressInfo] = None
    capacity: Optional[int] = None

@dataclass
class VmHardwareFloppyBackingInfo:
    type: VmHardwareFloppyBackingType
    auto_detect: Optional[bool] = None
    host_device: Optional[str] = None
    image_file: Optional[str] = None

@dataclass
class VmHardwareFloppyInfo:
    allow_guest_control: bool
    backing: VmHardwareFloppyBackingInfo
    label: str
    start_connected: bool
    state: VmHardwareConnectionState


@dataclass
class VmHardwareInfo:
    upgrade_policy: VmHardwareUpgradePolicy
    upgrade_status: VmHardwareUpgradeStatus
    version: VmHardwareVersion
    upgrade_error: Optional[dict] = None
    upgrade_version: Optional[VmHardwareVersion] = None


@dataclass
class VmHardwareAdapterScsiInfo:
    label: str
    scsi: VmHardwareScsiAddressInfo
    sharing: VmHardwareAdapterScsiSharing
    type: VmHardwareAdapterScsiType
    pci_slot_number: int

@dataclass
class VmHardwareBootInfo:
    delay: int
    enter_setup_mode: bool
    retry: bool
    retry_delay: int
    type: VmHardwareBootType
    network_protocol: VmHardwareBootNetworkProtocol
    efi_legacy_boot: Optional[bool] = None

@dataclass
class VmHardwareMemoryInfo:
    hot_add_enabled: bool
    size_MiB: int
    hot_add_increment_size_MiB: Optional[int] = None
    hot_add_limit_MiB: Optional[int] = None


@dataclass
class VmHardwareEthernetBackingInfo:
    type: VmHardwareEthernetBackingType
    connection_cookie: Optional[int] = None
    distributed_port: Optional[str] = None
    distributed_switch_uuid: Optional[str] = None
    host_device: Optional[str] = None
    network: Optional[str] = None
    network_name: Optional[str] = None
    opaque_network_id: Optional[str] = None
    opaque_network_type: Optional[str] = None

@dataclass
class VmHardwareEthernetInfo:
    allow_guest_control: bool
    backing: VmHardwareEthernetBackingInfo
    label: str
    mac_type: VmHardwareEthernetMacAddressType
    start_connected: bool
    state: VmHardwareConnectionState
    type: VmHardwareEthernetEmulationType
    wake_on_lan_enabled: bool
    mac_address: Optional[str] = None
    pci_slot_number: Optional[int] = None
    upt_compatibility_enabled: Optional[bool] = None

@dataclass
class VmHardwareAdapterSataInfo:
    bus: int
    label: str
    type: VmHardwareAdapterSataType
    pci_slot_number: Optional[int] = None

@dataclass
class VmHardwareParallelBackingInfo:
    type: VmHardwareParallelBackingType
    auto_detect: Optional[bool] = None
    file: Optional[str] = None
    host_device: Optional[str] = None

@dataclass
class VmHardwareParallelInfo:
    allow_guest_control: bool
    backing: VmHardwareParallelBackingInfo
    label: str
    start_connected: bool
    state: VmHardwareConnectionState

@dataclass
class VmHardwareAdapterNvmeInfo:
    bus: int
    label: str
    pci_slot_number: Optional[int] = None

@dataclass
class VmIdentityInfo:
    bios_uuid: str
    instance_uuid: str
    name: str

@dataclass
class VMInfo:
    serial_ports: List[VmHardwareSerialInfo]
    boot_devices: List[VmHardwareBootDeviceEntry]
    cdroms: List[VmHardwareCdromInfo]
    cpu: VmHardwareCpuInfo
    disks: List[VmHardwareDiskInfo]
    floppies: List[VmHardwareFloppyInfo]
    guest_OS: VmGuestOS
    hardware: VmHardwareInfo
    scsi_adapters: List[VmHardwareAdapterScsiInfo]
    boot: VmHardwareBootInfo
    memory: VmHardwareMemoryInfo
    name: str
    nics: List[VmHardwareEthernetInfo]
    sata_adapters: List[VmHardwareAdapterSataInfo]
    parallel_ports: List[VmHardwareParallelInfo]
    power_state: VmPowerState
    nvme_adapters: Optional[List[VmHardwareAdapterNvmeInfo]] = None
    identity: Optional[VmIdentityInfo] = None
    instant_clone_frozen: Optional[bool] = None

