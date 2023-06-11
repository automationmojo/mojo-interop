"""
.. module:: vmext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the VmExt object.

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

from typing import Optional, TYPE_CHECKING

from  http import HTTPStatus

from mojo.interop.services.vmware.vsphere.ext.baseext import BaseExt

if TYPE_CHECKING:
    from mojo.interop.services.vmware.vsphere.vsphereagent import VSphereAgent

class VmExt(BaseExt):

    def __init__(self, agent: "VSphereAgent"):
        super().__init__(agent)
        return

    def clone(self, source: str, name: str, power_on: bool=False, customizations: Optional[dict]=None):

        vminfo = None

        agent = self.agent

        body = {
            "name": name,
            "source": source,
            "power_on": power_on
        }

        if customizations is not None:
            body.update(customizations)

        req_url = agent.build_api_url(f"/vcenter/vm")

        resp = agent.session_post(req_url, json=body, action="clone")
        if resp.status_code == HTTPStatus.OK:
            vminfo = resp.json()
        else:
            resp.raise_for_status()

        return vminfo

    def delete(self, id: str):

        agent = self.agent

        req_url = agent.build_api_url(f"/vcenter/vm/{id}")

        resp = agent.session_delete(req_url)
        if resp.status_code != HTTPStatus.OK:
            resp.raise_for_status()

        return

    def get(self, id: str):

        vminfo = None

        agent = self.agent

        req_url = agent.build_api_url(f"/vcenter/vm/{id}")

        resp = agent.session_get(req_url)
        if resp.status_code == HTTPStatus.OK:
            vminfo = resp.json()
        else:
            resp.raise_for_status()

        return vminfo

    def instant_clone(self, source: str, name: str, placement: Optional[dict]=None, hwoptions: Optional[dict]=None):

        vminfo = None

        agent = self.agent

        body = {
            "name": name,
            "source": source,
        }

        if placement is not None:
            body["placement"] = placement

        if hwoptions is not None:
            body.update(hwoptions)

        req_url = agent.build_api_url(f"/vcenter/vm")

        resp = agent.session_post(req_url, json=body, action="clone")
        if resp.status_code == HTTPStatus.OK:
            vminfo = resp.json()
        else:
            resp.raise_for_status()

        return vminfo

    def list(self):

        vm_list = None

        agent = self.agent

        req_url = agent.build_api_url("/vcenter/vm")
        resp = agent.session_get(req_url)

        if resp.status_code == HTTPStatus.OK:
            vm_list = resp.json()
        else:
            resp.raise_for_status()

        return vm_list

    def register(self, name: str, storage: dict, placement: Optional[dict]=None):
        
        vminfo = None

        agent = self.agent

        body = {
            "name": name,
        }
        body.update(storage)

        if placement is not None:
            body.update(placement)

        req_url = agent.build_api_url(f"/vcenter/vm")

        resp = agent.session_post(req_url, json=body, action="register")
        if resp.status_code == HTTPStatus.OK:
            vminfo = resp.json()
        else:
            resp.raise_for_status()

        return vminfo
    
    def relocate(self, path: str, disks: Optional[dict]=None, placement: Optional[dict]=None):
        
        vminfo = None

        agent = self.agent

        body = {
            "path": path,
        }
        
        if disks is not None:
            body["disks"] = disks

        if placement is not None:
            body.update(placement)

        req_url = agent.build_api_url(f"/vcenter/vm")

        resp = agent.session_post(req_url, json=body, action="relocate")
        if resp.status_code == HTTPStatus.OK:
            vminfo = resp.json()
        else:
            resp.raise_for_status()

        return vminfo

    def unregister(self, vmid: str):
        
        agent = self.agent

        req_url = agent.build_api_url(f"/vcenter/vm")

        resp = agent.session_post(req_url, action="unregister", vm=vmid)
        if resp.status_code == HTTPStatus.OK:
            vminfo = resp.json()
        else:
            resp.raise_for_status()

        return
