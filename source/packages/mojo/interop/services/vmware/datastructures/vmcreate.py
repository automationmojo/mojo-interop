"""
.. module:: vmcreatespec
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains various VmCreateSpec related objects used in the creation of VM(s).

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

from typing import List, Optional

from dataclasses import dataclass

from mojo.interop.services.vmware.metasphere.vmguestos import VmGuestOS
from mojo.interop.services.vmware.metasphere.vmhardware import VmHardwareVersion

from mojo.interop.services.vmware.datastructures.vmplacement import VmPlacementSpec
from mojo.interop.services.vmware.datastructures.vmhardware import (
    VmHardwareBootCreateSpec,
    VmHardwareCpuUpdateSpec,
    VmHardwareDiskCreateSpec,
    VmHardwareFloppyCreateSpec,
    VmHardwareCdromCreateSpec,
    VmHardwareMemoryUpdateSpec,
    VmHardwareEthernetCreateSpec,
    VmHardwareAdapterNvmeCreateSpec,
    VmHardwareParallelCreateSpec,
    VmHardwareBootDeviceEntryCreateSpec,
    VmHardwareAdapterSataCreateSpec,
    VmHardwareAdapterScsiCreateSpec,
    VmHardwareSerialCreateSpec
)
from mojo.interop.services.vmware.datastructures.vmstorage import VmStoragePolicySpec

@dataclass
class VmCreateSpec:
    guest_OS: VmGuestOS
    placement: VmPlacementSpec
    boot: Optional[VmHardwareBootCreateSpec]
    cpu: Optional[VmHardwareCpuUpdateSpec]
    disks: Optional[List[VmHardwareDiskCreateSpec]]
    floppies: Optional[List[VmHardwareFloppyCreateSpec]]
    cdroms: Optional[List[VmHardwareCdromCreateSpec]]
    hardware_version: Optional[VmHardwareVersion]
    memory: Optional[VmHardwareMemoryUpdateSpec]
    name: Optional[str]
    nics: Optional[List[VmHardwareEthernetCreateSpec]]
    nvme_adapters: Optional[List[VmHardwareAdapterNvmeCreateSpec]]
    parallel_ports: Optional[List[VmHardwareParallelCreateSpec]]
    boot_devices: Optional[List[VmHardwareBootDeviceEntryCreateSpec]]
    sata_adapters: Optional[List[VmHardwareAdapterSataCreateSpec]]
    scsi_adapters: Optional[List[VmHardwareAdapterScsiCreateSpec]]
    serial_ports: Optional[List[VmHardwareSerialCreateSpec]]
    storage_policy: Optional[List[VmStoragePolicySpec]]
