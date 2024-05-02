"""
.. module:: vmhardware
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains various VM hardware related enumerations.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []

class VmHardwareVersion:
    VMX_03 = "VMX_03"
    VMX_04 = "VMX_04"
    VMX_06 = "VMX_06"
    VMX_07 = "VMX_07"
    VMX_08 = "VMX_08"
    VMX_09 = "VMX_09"
    VMX_10 = "VMX_10"
    VMX_11 = "VMX_11"
    VMX_12 = "VMX_12"
    VMX_13 = "VMX_13"
    VMX_14 = "VMX_14"
    VMX_15 = "VMX_15"
    VMX_16 = "VMX_16"
    VMX_17 = "VMX_17"
    VMX_18 = "VMX_18"
    VMX_19 = "VMX_19"
    VMX_20 = "VMX_20"

class VmHardwareBootNetworkProtocol:
    IPV4 = "IPV4"
    IPV6 = "IPV6"

class VmHardwareBootType:
    BIOS = "BIOS"
    EFI = "EFI"

class VmHardwareDiskBackingType:
    VMDK_FILE = "VMDK_FILE"

class VmHardwareDiskHostBusAdapterType:
    IDE = "IDE"
    SCSI = "SCSI"
    SATA = "SATA"
    NVME = "NVME"

class VmHardwareFloppyBackingType:
    IMAGE_FILE = "IMAGE_FILE"
    HOST_DEVICE = "HOST_DEVICE"
    CLIENT_DEVICE = "CLIENT_DEVICE"

class VmHardwareCdromDeviceAccessType:
    EMULATION = "EMULATION"
    PASSTHRU = "PASSTHRU"
    PASSTHRU_EXCLUSIVE = "PASSTHRU_EXCLUSIVE"

class VmHardwareCdromBackingType:
    ISO_FILE = "ISO_FILE"
    HOST_DEVICE = "HOST_DEVICE"
    CLIENT_DEVICE = "CLIENT_DEVICE"

class VmHardwareCdromHostBusAdapterType:
    IDE = "IDE"
    SATA = "SATA"

class VmHardwareEthernetBackingType:
    STANDARD_PORTGROUP = "STANDARD_PORTGROUP"
    HOST_DEVICE = "HOST_DEVICE"
    DISTRIBUTED_PORTGROUP = "DISTRIBUTED_PORTGROUP"
    OPAQUE_NETWORK = "OPAQUE_NETWORK"

class VmHardwareEthernetMacAddressType:
    MANUAL = "MANUAL"
    GENERATED = "GENERATED"
    ASSIGNED = "ASSINGED"

class VmHardwareEthernetEmulationType:
    E1000 = "E1000"
    E1000E = "E1000E"
    PCNET32 = "PCNET32"
    VMXNET = "VMXNET"
    VMXNET2 = "VMXNET2"
    VMXNET3 = "VMXNET3"

class VmHardwareParallelBackingType:
    FILE = "FILE"
    HOST_DEVICE = "HOST_DEVICE"

class VmHardwareBootDeviceType:
    CDROM = "CDROM"
    DISK = "DISK"
    ETHERNET = "ETHERNET"
    FLOPPY = "FLOPPY"

class VmHardwareAdapterSataType:
    AHCI = "AHCI"

class VmHardwareAdapterScsiSharing:
    NONE = "NONE"
    VIRTUAL = "VIRTUAL"
    PHYSICAL = "PHYSICAL"

class VmHardwareAdapterScsiType:
    BUSLOGIC = "BUSLOGIC"
    LSILOGIC = "LSILOGIC"
    LSILOGICSAS = "LSILOGICSAS"
    PVSCSI = "PVSCSI"

class VmHardwareSerialBackingType:
    FILE = "FILE"
    HOST_DEVICE = "HOST_DEVICE"
    PIPE_SERVER = "PIPE_SERVER"
    PIPE_CLIENT = "PIPE_CLIENT"
    NETWORK_SERVER = "NETWORK_SERVER"
    NETWORK_CLIENT = "NETWORK_CLIENT"

class VmHardwareConnectionState:
    CONNECTED = "CONNECTED"
    RECOVERABLE_ERROR = "RECOVERABLE_ERROR"
    UNRECOVERABLE_ERROR = "UNRECOVERABLE_ERROR"
    NOT_CONNECTED = "NOT_CONNECTED"
    UNKNOWN = "UNKNOWN"

class VmHardwareUpgradePolicy:
    NEVER = "NEVER"
    AFTER_CLEAN_SHUTDOWN = "AFTER_CLEAN_SHUTDOWN"
    ALWAYS = "ALWAYS"

class VmHardwareUpgradeStatus:
    NONE = "NONE"
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class VmHardwareAdapterScsiSharing:
    NONE = "NONE"
    VIRTUAL = "VIRTUAL"
    PHYSICAL = "PHYSICAL"

class VmPowerState:
    POWERED_OFF = "POWERED_OFF"
    POWERED_ON = "POWERED_ON"
    SUSPENDED = "SUSPENDED"