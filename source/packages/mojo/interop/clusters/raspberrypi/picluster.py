"""
.. module:: picluster
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the PiCluster object.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []
__version__ = "1.0.0"
__maintainer__ = "Myron Walker"
__email__ = "myron.walker@gmail.com"
__status__ = "Development" # Prototype, Development or Production
__license__ = "MIT"

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
