
from typing import TYPE_CHECKING

from  http import HTTPStatus

from mojo.interop.services.vmware.vsphere.ext.baseext import BaseExt

if TYPE_CHECKING:
    from mojo.interop.services.vmware.vsphere.vsphereagent import VSphereAgent

class FolderExt(BaseExt):

    def __init__(self, agent: "VSphereAgent"):
        super().__init__(agent)
        return
    
    def list(self):
        folder_list = None

        agent = self.agent

        req_url = agent.build_api_url("/vcenter/folder")
        resp = agent.session_get(req_url)

        if resp.status_code == HTTPStatus.OK:
            folder_list = resp.json()
        else:
            resp.raise_for_status()

        return folder_list
