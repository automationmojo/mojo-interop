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

from mojo.interop.services.vmware.datastructures.specs.vmplacement import VmPlacementSpec
from mojo.interop.services.vmware.datastructures.specs.vmhardware import (
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
from mojo.interop.services.vmware.datastructures.specs.vmstorage import VmStoragePolicySpec

@dataclass
class VmCreateSpec:
    guest_OS: VmGuestOS
    placement: VmPlacementSpec
    boot: Optional[VmHardwareBootCreateSpec] = None
    cpu: Optional[VmHardwareCpuUpdateSpec] = None
    disks: Optional[List[VmHardwareDiskCreateSpec]] = None
    floppies: Optional[List[VmHardwareFloppyCreateSpec]] = None
    cdroms: Optional[List[VmHardwareCdromCreateSpec]] = None
    hardware_version: Optional[VmHardwareVersion] = None
    memory: Optional[VmHardwareMemoryUpdateSpec] = None
    name: Optional[str] = None
    nics: Optional[List[VmHardwareEthernetCreateSpec]] = None
    nvme_adapters: Optional[List[VmHardwareAdapterNvmeCreateSpec]] = None
    parallel_ports: Optional[List[VmHardwareParallelCreateSpec]] = None
    boot_devices: Optional[List[VmHardwareBootDeviceEntryCreateSpec]] = None
    sata_adapters: Optional[List[VmHardwareAdapterSataCreateSpec]] = None
    scsi_adapters: Optional[List[VmHardwareAdapterScsiCreateSpec]] = None
    serial_ports: Optional[List[VmHardwareSerialCreateSpec]] = None
    storage_policy: Optional[List[VmStoragePolicySpec]] = None
