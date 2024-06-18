"""
.. module:: picluster
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the PiCluster object.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []


from typing import Dict

from mojo.landscaping.cluster.nodebase import NodeBase
from mojo.landscaping.landscapedevicecluster import LandscapeDeviceCluster
from mojo.landscaping.landscapedevicegroup import LandscapeDeviceGroup

class PiCluster(LandscapeDeviceCluster):
    """
    """

    def __init__(self, label: str, nodes: Dict[str, NodeBase], spares: Dict[str, NodeBase],
                 group: LandscapeDeviceGroup) -> None:
        super().__init__(label, nodes, spares, group)
        return
