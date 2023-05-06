"""
.. module:: pinodecoordinator
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the PiNodeCoordinator which is used for managing connectivity with raspberry
               pi computer nodes in a raspberry pi cluster.

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

from typing import TYPE_CHECKING

from mojo.xmods.landscaping.cluster.nodecoordinatorbase import NodeCoordinatorBase

from mojo.interop.clusters.constants import INTEGRATION_CLASS_FOR_RASPBERRYPI_NODE
from mojo.interop.clusters.raspberrypi.pinode import PiNode
from mojo.interop.clusters.raspberrypi.picluster import PiCluster

if TYPE_CHECKING:
    from mojo.xmods.landscaping.landscape import Landscape

class PiNodeCoordinator(NodeCoordinatorBase):
    """
        The :class:`LinuxPoolCoordinator` creates a pool of agents that can be used to
        coordinate the interop activities of the automation process and remote Linux
        client.
    """

    INTEGRATION_CLASS = INTEGRATION_CLASS_FOR_RASPBERRYPI_NODE
    CLIENT_TYPE = PiNode
    CLUSTER_TYPE = PiCluster

    # pylint: disable=attribute-defined-outside-init

    def __init__(self, lscape: "Landscape", *args, **kwargs):
        super().__init__(lscape, *args, **kwargs)
        return
