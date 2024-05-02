"""
.. module:: windowsclientcoordinatorcoupling
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains a WindowsClientCoordinatorCoupling object to use for working with the Windows clients.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []



from typing import TYPE_CHECKING

from mojo.landscaping.client.clientcoordinatorcouplingbase import ClientCoordinatorCouplingBase

from mojo.interop.clients.constants import INTEGRATION_CLASS_FOR_WINDOWS_CLIENT
from mojo.interop.clients.windows.windowsclientcoordinator import WindowsClientCoordinator


class WindowsClientCoordinatorCoupling(ClientCoordinatorCouplingBase):
    """
        The WindowsClientCoordinatorCoupling handle the requirement registration for the Windows coordinator.
    """

    COORDINATOR_TYPE = WindowsClientCoordinator

    integration_root: str = "apod"
    integration_section: str = "clients"
    integration_leaf: str = "deviceType"
    integration_class: str = INTEGRATION_CLASS_FOR_WINDOWS_CLIENT

    def __init__(self, *args, **kwargs):
        """
            The default contructor for an :class:`WindowsCoordinatorIntegration`.
        """
        super().__init__(*args, **kwargs)
        return
