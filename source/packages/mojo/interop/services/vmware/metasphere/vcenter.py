
from enum import Enum

class FolderType(str, Enum):
    DATACENTER = "DATACENTER"
    DATASTORE = "DATASTORE"
    HOST = "HOST"
    NETWORK = "NETWORK"
    VIRTUAL_MACHINE = "VIRTUAL_MACHINE"

class VmPowerState(str, Enum):
    POWERED_OFF = "POWERED_OFF"
    POWERED_ON = "POWERED_ON"
    SUSPENDED = "SUSPENDED"
