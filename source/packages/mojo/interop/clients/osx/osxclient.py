
from typing import TYPE_CHECKING

from mojo.xmods.landscaping.friendlyidentifier import FriendlyIdentifier
from mojo.xmods.landscaping.client.clientbase import ClientBase


if TYPE_CHECKING:
    from mojo.xmods.landscaping.landscape import Landscape
    from mojo.xmods.landscaping.coordinators.coordinatorbase import CoordinatorBase

class OsxClient(ClientBase):

    def __init__(self, lscape: "Landscape", coordinator: "CoordinatorBase",
                 friendly_id:FriendlyIdentifier, device_type: str, device_config: dict):
        super().__init__(lscape, coordinator, friendly_id, device_type, device_config)
        return
