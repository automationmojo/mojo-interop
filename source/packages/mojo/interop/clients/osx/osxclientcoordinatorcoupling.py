"""
.. module:: osxclientcoordinatorcoupling
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains a OsxClientCoordinatorCoupling object to use for working with the OSX clients.

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

from mojo.xmods.landscaping.client.clientcoordinatorcouplingbase import ClientCoordinatorCouplingBase

from mojo.interop.clients.constants import INTEGRATION_CLASS_FOR_OSX_CLIENT
from mojo.interop.clients.osx.osxclientcoordinator import OsxClientCoordinator


class OsxClientCoordinatorCoupling(ClientCoordinatorCouplingBase):
    """
        The OsxClientCoordinatorCoupling handle the requirement registration for the OSX coordinator.
    """

    COORDINATOR_TYPE = OsxClientCoordinator

    integration_root: str = "apod"
    integration_section: str = "devices"
    integration_leaf: str = "deviceType"
    integration_class: str = INTEGRATION_CLASS_FOR_OSX_CLIENT

    def __init__(self, *args, **kwargs):
        """
            The default contructor for an :class:`OsxCoordinatorIntegration`.
        """
        super().__init__(*args, **kwargs)
        return
