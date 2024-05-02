"""
.. module:: isoext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the IsoExt object.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []


from typing import TYPE_CHECKING

from  http import HTTPStatus

from mojo.interop.services.vmware.vsphere.ext.baseext import BaseExt

if TYPE_CHECKING:
    from mojo.interop.services.vmware.vsphere.vsphereagent import VSphereAgent

class IsoExt(BaseExt):

    def __init__(self, agent: "VSphereAgent"):
        super().__init__(agent)
        return
    
    def mount(self, vm: str, library_item: str):
        result = None

        agent = self.agent

        body = {
            "vm": vm,
            "library_item": library_item
        }

        req_url = agent.build_api_url("/vcenter/iso/image")
        resp = agent.session_post(req_url, json=body, action="mount")

        if resp.status_code == HTTPStatus.OK:
            result = resp.json()
        else:
            resp.raise_for_status()

        return result
    
    def unmount(self, vm: str, cdrom: str):
        result = None

        agent = self.agent

        body = {
            "vm": vm,
            "cdrom": cdrom
        }

        req_url = agent.build_api_url("/vcenter/iso/image")
        resp = agent.session_post(req_url, json=body, action="unmount")

        if resp.status_code == HTTPStatus.OK:
            result = resp.json()
        else:
            resp.raise_for_status()

        return result