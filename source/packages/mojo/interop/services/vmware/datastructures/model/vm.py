__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []


from typing import List, Optional

from dataclasses import dataclass

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

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareSerialBackingInfo":
        obj = VmHardwareSerialBackingInfo(**info)
        return obj
    

@dataclass
class VmHardwareSerialInfo:
    allow_guest_control: bool
    backing: VmHardwareSerialBackingInfo
    label: str
    start_connected: bool
    state: VmHardwareConnectionState
    yield_on_poll: bool

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareSerialInfo":
        info["backing"] = VmHardwareSerialBackingInfo.from_dict(info["backing"])
        obj = VmHardwareSerialInfo(**info)
        return obj

@dataclass
class VmHardwareBootDeviceEntry:
    type: VmHardwareBootDeviceType
    disks: List[str]
    nic: str

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareBootDeviceEntry":
        obj = VmHardwareBootDeviceEntry(**info)
        return obj

@dataclass
class VmHardwareCdromBackingInfo:
    iso_file: str
    type: VmHardwareCdromBackingType
    auto_detect: Optional[bool] = None
    device_access_type: Optional[VmHardwareCdromDeviceAccessType] = None
    host_device: Optional[str] = None

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareCdromBackingInfo":
        obj = VmHardwareCdromBackingInfo(**info)
        return obj

@dataclass
class VmHardwareIdeAddressInfo:
    master: bool
    primary: bool

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareIdeAddressInfo":
        obj = VmHardwareIdeAddressInfo(**info)
        return obj

@dataclass
class VmHardwareNvmeAddressInfo:
    bus: int
    unit: int

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareNvmeAddressInfo":
        obj = VmHardwareNvmeAddressInfo(**info)
        return obj


@dataclass
class VmHardwareSataAddressInfo:
    bus: int
    unit: int

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareSataAddressInfo":
        obj = VmHardwareSataAddressInfo(**info)
        return obj

@dataclass
class VmHardwareScsiAddressInfo:
    bus: int
    unit: int

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareScsiAddressInfo":
        obj = VmHardwareScsiAddressInfo(**info)
        return obj

@dataclass
class VmHardwareCdromInfo:
    allow_guest_control: bool
    backing: VmHardwareCdromBackingInfo
    label: str
    start_connected: bool
    state: VmHardwareConnectionState
    type: VmHardwareCdromHostBusAdapterType
    ide: Optional[VmHardwareIdeAddressInfo] = None
    sata: Optional[VmHardwareSataAddressInfo] = None

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareCdromInfo":
        info["backing"] = VmHardwareCdromBackingInfo.from_dict(info["backing"])
        if "ide" in info:
            info["ide"] = VmHardwareIdeAddressInfo.from_dict(info["ide"])
        if "sata" in info:
            info["sata"] = VmHardwareSataAddressInfo.from_dict(info["sata"])
        obj = VmHardwareCdromInfo(**info)
        return obj

@dataclass
class VmHardwareCpuInfo:
    cores_per_socket: int
    count: int
    hot_add_enabled: bool
    hot_remove_enabled: bool

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareCpuInfo":
        obj = VmHardwareCpuInfo(**info)
        return obj

@dataclass
class VmHardwareDiskBackingInfo:
    type: VmHardwareDiskBackingType
    vmdk_file: str

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareDiskBackingInfo":
        obj = VmHardwareDiskBackingInfo(**info)
        return obj

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

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareCdromInfo":
        info["backing"] = VmHardwareDiskBackingInfo.from_dict(info["backing"])
        if "ide" in info:
            info["ide"] = VmHardwareIdeAddressInfo.from_dict(info["ide"])
        if "nvme" in info:
            info["nvme"] = VmHardwareNvmeAddressInfo.from_dict(info["nvme"])
        if "sata" in info:
            info["sata"] = VmHardwareSataAddressInfo.from_dict(info["sata"])
        if "scsi" in info:
            info["scsi"] = VmHardwareScsiAddressInfo.from_dict(info["scsi"])
        obj = VmHardwareDiskInfo(**info)
        return obj

@dataclass
class VmHardwareFloppyBackingInfo:
    type: VmHardwareFloppyBackingType
    auto_detect: Optional[bool] = None
    host_device: Optional[str] = None
    image_file: Optional[str] = None

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareFloppyBackingInfo":
        obj = VmHardwareFloppyBackingInfo(**info)
        return obj

@dataclass
class VmHardwareFloppyInfo:
    allow_guest_control: bool
    backing: VmHardwareFloppyBackingInfo
    label: str
    start_connected: bool
    state: VmHardwareConnectionState

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareFloppyInfo":
        info["backing"] = VmHardwareFloppyBackingInfo.from_dict(info["backing"])
        obj = VmHardwareFloppyInfo(**info)
        return obj


@dataclass
class VmHardwareInfo:
    upgrade_policy: VmHardwareUpgradePolicy
    upgrade_status: VmHardwareUpgradeStatus
    version: VmHardwareVersion
    upgrade_error: Optional[dict] = None
    upgrade_version: Optional[VmHardwareVersion] = None

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareInfo":
        obj = VmHardwareInfo(**info)
        return obj

@dataclass
class VmHardwareAdapterScsiInfo:
    label: str
    scsi: VmHardwareScsiAddressInfo
    sharing: VmHardwareAdapterScsiSharing
    type: VmHardwareAdapterScsiType
    pci_slot_number: int

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareAdapterScsiInfo":
        info["scsi"] = VmHardwareScsiAddressInfo.from_dict(info["scsi"])
        obj = VmHardwareAdapterScsiInfo(**info)
        return obj

@dataclass
class VmHardwareBootInfo:
    delay: int
    enter_setup_mode: bool
    retry: bool
    retry_delay: int
    type: VmHardwareBootType
    network_protocol: Optional[VmHardwareBootNetworkProtocol] = None
    efi_legacy_boot: Optional[bool] = None

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareBootInfo":
        obj = VmHardwareBootInfo(**info)
        return obj

@dataclass
class VmHardwareMemoryInfo:
    hot_add_enabled: bool
    size_MiB: int
    hot_add_increment_size_MiB: Optional[int] = None
    hot_add_limit_MiB: Optional[int] = None

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareMemoryInfo":
        obj = VmHardwareMemoryInfo(**info)
        return obj


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

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareEthernetBackingInfo":
        obj = VmHardwareEthernetBackingInfo(**info)
        return obj

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

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareEthernetInfo":
        info["backing"] = VmHardwareEthernetBackingInfo.from_dict(info["backing"])
        obj = VmHardwareEthernetInfo(**info)
        return obj

@dataclass
class VmHardwareAdapterSataInfo:
    bus: int
    label: str
    type: VmHardwareAdapterSataType
    pci_slot_number: Optional[int] = None

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareAdapterSataInfo":
        obj = VmHardwareAdapterSataInfo(**info)
        return obj

@dataclass
class VmHardwareParallelBackingInfo:
    type: VmHardwareParallelBackingType
    auto_detect: Optional[bool] = None
    file: Optional[str] = None
    host_device: Optional[str] = None

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareParallelBackingInfo":
        obj = VmHardwareParallelBackingInfo(**info)
        return obj

@dataclass
class VmHardwareParallelInfo:
    allow_guest_control: bool
    backing: VmHardwareParallelBackingInfo
    label: str
    start_connected: bool
    state: VmHardwareConnectionState

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareParallelInfo":
        info["backing"] = VmHardwareParallelBackingInfo.from_dict(info["backing"])
        obj = VmHardwareParallelInfo(**info)
        return obj

@dataclass
class VmHardwareAdapterNvmeInfo:
    bus: int
    label: str
    pci_slot_number: Optional[int] = None

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareAdapterNvmeInfo":
        obj = VmHardwareAdapterNvmeInfo(**info)
        return obj

@dataclass
class VmIdentityInfo:
    bios_uuid: str
    instance_uuid: str
    name: str

    @classmethod
    def from_dict(cls, info: dict) -> "VmIdentityInfo":
        obj = VmIdentityInfo(**info)
        return obj

@dataclass
class VmInfo:
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

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareAdapterNvmeInfo":

        info["serial_ports"] = [VmHardwareSerialInfo.from_dict(item) for item in info["serial_ports"]]
        info["boot_devices"] = [VmHardwareBootDeviceEntry.from_dict(item) for item in info["boot_devices"]]
        info["cdroms"] = { key: VmHardwareCdromInfo.from_dict(item) for key, item in info["cdroms"].items() }
        info["cpu"] = VmHardwareCpuInfo.from_dict(info["cpu"])
        info["disks"] = { key: VmHardwareDiskInfo.from_dict(item) for key, item in info["disks"].items() }
        info["floppies"] = { key: VmHardwareFloppyInfo.from_dict(item) for key, item in info["floppies"].items() }
        info["hardware"] = VmHardwareInfo.from_dict(info["hardware"])
        info["scsi_adapters"] = { key: VmHardwareAdapterScsiInfo.from_dict(item) for key, item in info["scsi_adapters"].items() }
        info["boot"] = VmHardwareBootInfo.from_dict(info["boot"])
        info["memory"] = VmHardwareMemoryInfo.from_dict(info["memory"])
        info["nics"] = { key: VmHardwareEthernetInfo.from_dict(item) for key, item in info["nics"].items() }
        info["sata_adapters"] = { key: VmHardwareAdapterSataInfo.from_dict(item) for key, item in info["sata_adapters"].items() }
        info["parallel_ports"] = { key: VmHardwareParallelInfo.from_dict(item) for key, item in info["parallel_ports"].items() }
        if "nvme_adapters" in info:
            info["nvme_adapters"] = { key: VmHardwareAdapterNvmeInfo.from_dict(item) for key, item in info["nvme_adapters"].items() }
        if "identity" in info:
            info["identity"] = VmIdentityInfo.from_dict(info["identity"])

        obj = VmHardwareAdapterNvmeInfo(**info)
        return obj