"""
.. module:: baseext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the BaseExt object used share common functionality between vshere agent extensions.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []


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
