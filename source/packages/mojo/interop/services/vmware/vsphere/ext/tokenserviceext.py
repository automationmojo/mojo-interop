
from typing import TYPE_CHECKING

from  http import HTTPStatus

from mojo.interop.services.vmware.vsphere.ext.baseext import BaseExt

if TYPE_CHECKING:
    from mojo.interop.services.vmware.vsphere.vsphereagent import VSphereAgent

class TokenServiceExt(BaseExt):

    def __init__(self, agent: "VSphereAgent"):
        super().__init__(agent)
        return