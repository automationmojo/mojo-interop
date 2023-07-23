
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