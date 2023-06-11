
from typing import TYPE_CHECKING

import weakref


if TYPE_CHECKING:
    from mojo.interop.services.vmware.vsphere.vsphereagent import VSphereAgent

class BaseExt:

    def __init__(self, agent: "VSphereAgent"):
        self._agent_ref = weakref.ref(agent)
        return
    
    @property
    def agent(self) -> "VSphereAgent":
        return self._agent_ref()
