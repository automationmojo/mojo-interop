
from typing import TYPE_CHECKING

from  http import HTTPStatus

from mojo.interop.services.vmware.vsphere.ext.baseext import BaseExt

if TYPE_CHECKING:
    from mojo.interop.services.vmware.vsphere.vsphereagent import VSphereAgent

class DataCenterExt(BaseExt):

    def __init__(self, agent: "VSphereAgent"):
        super().__init__(agent)
        return
    
    def delete(self, name: str):

        agent = self.agent

        req_url = agent.build_api_url(f"/vcenter/datacenter/{name}")
        resp = agent.session_delete(req_url)

        if resp.status_code != HTTPStatus.OK:
            resp.raise_for_status()
        
        return

    def get(self, name: str):

        dcinfo = None

        agent = self.agent

        req_url = agent.build_api_url(f"/vcenter/datacenter/{name}")

        resp = agent.session_get(req_url)
        if resp.status_code == HTTPStatus.OK:
            dcinfo = resp.json()
        else:
            resp.raise_for_status()

        return dcinfo

    def list(self):
        datacenter_list = None

        agent = self.agent

        req_url = agent.build_api_url("/vcenter/datacenter")
        resp = agent.session_get(req_url)

        if resp.status_code == HTTPStatus.OK:
            datacenter_list = resp.json()
        else:
            resp.raise_for_status()

        return datacenter_list
