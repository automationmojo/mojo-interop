
from typing import Dict

from mojo.xmods.landscaping.cluster.nodebase import NodeBase
from mojo.xmods.landscaping.landscapedevicecluster import LandscapeDeviceCluster
from mojo.xmods.landscaping.landscapedevicegroup import LandscapeDeviceGroup

class PiCluster(LandscapeDeviceCluster):
    """
    """

    def __init__(self, label: str, nodes: Dict[NodeBase], spares: Dict[NodeBase],
                 group: LandscapeDeviceGroup) -> None:
        super().__init__(label, nodes, spares, group)
        return
