

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []

from dataclasses import dataclass

from mojo.interop.services.vmware.metasphere.vcenter import FolderType

@dataclass
class DatacenterSummary:
    name: str
    datacenter: str

@dataclass
class FolderSummary:
    name: str
    folder: str
    type: FolderType
