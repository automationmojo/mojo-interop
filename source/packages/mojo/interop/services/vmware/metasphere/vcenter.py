
from enum import Enum

class FolderType(str, Enum):
    DATACENTER = "DATACENTER"
    DATASTORE = "DATASTORE"
    HOST = "HOST"
    NETWORK = "NETWORK"
    VIRTUAL_MACHINE = "VIRTUAL_MACHINE"

