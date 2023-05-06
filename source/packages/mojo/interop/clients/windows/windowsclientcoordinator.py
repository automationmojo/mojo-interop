"""
.. module:: windowsclientcoordinator
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the WindowsPoolCoordinator which is used for managing connectivity with pools of Windows capable devices

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

from mojo.xmods.landscaping.client.clientcoordinatorbase import ClientCoordinatorBase

from mojo.interop.clients.constants import INTEGRATION_CLASS_FOR_WINDOWS_CLIENT
from mojo.interop.clients.windows.windowsclient import WindowsClient

if TYPE_CHECKING:
    from mojo.xmods.landscaping.landscape import Landscape

class WindowsClientCoordinator(ClientCoordinatorBase):
    """
        The :class:`WindowsPoolCoordinator` creates a pool of agents that can be used to
        coordinate the interop activities of the automation process and remote Windows
        client.
    """

    INTEGRATION_CLASS = INTEGRATION_CLASS_FOR_WINDOWS_CLIENT
    CLIENT_TYPE = WindowsClient

    # pylint: disable=attribute-defined-outside-init

    def __init__(self, lscape: "Landscape", *args, **kwargs):
        super().__init__(lscape, *args, **kwargs)
        return
