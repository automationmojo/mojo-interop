"""
.. module:: pinodecoordinatorcoupling
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains a PiNodeCoordinatorCoupling object to use for working with the raspberry
               pi 'PiNode' cluster nodes.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []



from typing import TYPE_CHECKING

from mojo.interop.clusters.constants import INTEGRATION_CLASS_FOR_RASPBERRYPI_NODE
from mojo.landscaping.cluster.nodecoordinatorcouplingbase import NodeCoordinatorCouplingBase


class PiNodeCoordinatorCoupling(NodeCoordinatorCouplingBase):
    """
        The LinuxClientCoordinatorCoupling handle the requirement registration for the Linux coordinator.
    """

    integration_class: str = INTEGRATION_CLASS_FOR_RASPBERRYPI_NODE

    def __init__(self, *args, **kwargs):
        """
            The default contructor for an :class:`LinuxCoordinatorIntegration`.
        """
        super().__init__(*args, **kwargs)
        return