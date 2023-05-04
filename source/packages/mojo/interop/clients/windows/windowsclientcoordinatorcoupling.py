"""
.. module:: windowsclientcoordinatorcoupling
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains a WindowsClientCoordinatorCoupling object to use for working with the Windows clients.

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

from mojo.interop.clients.constants import INTEGRATION_CLASS_FOR_WINDOWS_CLIENT
from mojo.interop.clients.base.baseclientcoordinatorcoupling import BaseClientCoordinatorCoupling

class WindowsClientCoordinatorCoupling(BaseClientCoordinatorCoupling):
    """
        The WindowsClientCoordinatorCoupling handle the requirement registration for the Windows coordinator.
    """

    pathbase = "/windows"

    integration_section: str = "devices"
    integration_leaf: str = "deviceType"
    integration_class: str = INTEGRATION_CLASS_FOR_WINDOWS_CLIENT

    def __init__(self, *args, **kwargs):
        """
            The default contructor for an :class:`WindowsCoordinatorIntegration`.
        """
        super().__init__(*args, **kwargs)
        return
