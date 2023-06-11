
from typing import List, Optional

import weakref

from  http import HTTPStatus

from mojo.xmods.credentials.basiccredential import BasicCredential

import requests

#Deployment
#Iso
#Storage

class DataCenterExt:

    def __init__(self, agent: "VSphereAgent"):
        self._agent_ref = weakref.ref(agent)
        return
    
    @property
    def agent(self) -> "VSphereAgent":
        return self._agent_ref()
    
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


class DataStoreExt:

    def __init__(self, agent: "VSphereAgent"):
        self._agent_ref = weakref.ref(agent)
        return
    
    @property
    def agent(self) -> "VSphereAgent":
        return self._agent_ref()
    
    def get(self, name: str):

        dsinfo = None

        agent = self.agent

        req_url = agent.build_api_url(f"/vcenter/datastore/{name}")

        resp = agent.session_get(req_url)
        if resp.status_code == HTTPStatus.OK:
            dsinfo = resp.json()
        else:
            resp.raise_for_status()

        return dsinfo

    def list(self):
        datastore_list = None

        agent = self.agent

        req_url = agent.build_api_url("/vcenter/datastore")
        resp = agent.session_get(req_url)

        if resp.status_code == HTTPStatus.OK:
            datastore_list = resp.json()
        else:
            resp.raise_for_status()

        return datastore_list


class FolderExt:

    def __init__(self, agent: "VSphereAgent"):
        self._agent_ref = weakref.ref(agent)
        return
    
    @property
    def agent(self) -> "VSphereAgent":
        return self._agent_ref()
    
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


class HostExt:

    def __init__(self, agent: "VSphereAgent"):
        self._agent_ref = weakref.ref(agent)
        return
    
    @property
    def agent(self) -> "VSphereAgent":
        return self._agent_ref()
    
    def connect(self, host: str):

        agent = self.agent

        req_url = agent.build_api_url(f"/vcenter/host/{host}")
        resp = agent.session_post(req_url, action="connect")

        if resp.status_code != HTTPStatus.OK:
            resp.raise_for_status()
        
        return

    def delete(self, host: str):

        agent = self.agent

        req_url = agent.build_api_url(f"/vcenter/host/{host}")
        resp = agent.session_delete(req_url)

        if resp.status_code != HTTPStatus.OK:
            resp.raise_for_status()
        
        return

    def disconnect(self, host: str):

        agent = self.agent

        req_url = agent.build_api_url(f"/vcenter/host/{host}")
        resp = agent.session_post(req_url, action="disconnect")

        if resp.status_code != HTTPStatus.OK:
            resp.raise_for_status()
        
        return

    def list(self):
        host_list = None

        agent = self.agent

        req_url = agent.build_api_url("/vcenter/host")
        resp = agent.session_get(req_url)

        if resp.status_code == HTTPStatus.OK:
            host_list = resp.json()
        else:
            resp.raise_for_status()

        return host_list


class NetworkExt:

    def __init__(self, agent: "VSphereAgent"):
        self._agent_ref = weakref.ref(agent)
        return
    
    @property
    def agent(self) -> "VSphereAgent":
        return self._agent_ref()
    
    def list(self):
        network_list = None

        agent = self.agent

        req_url = agent.build_api_url("/vcenter/network")
        resp = agent.session_get(req_url)

        if resp.status_code == HTTPStatus.OK:
            network_list = resp.json()
        else:
            resp.raise_for_status()

        return network_list



class VmExt:

    def __init__(self, agent: "VSphereAgent"):
        self._agent_ref = weakref.ref(agent)
        return
    
    @property
    def agent(self) -> "VSphereAgent":
        return self._agent_ref()

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


class VSphereAgent:

    def __init__(self, host: str, credential: BasicCredential, verify_certificates: bool=False):
        
        self._session = requests.session()
        self._session.verify = verify_certificates

        self._host = host
        self._credential = credential
        
        self._api_root = f"https://{host}/api"
        self._rest_root = f"https://{host}/rest" 

        self._auth_token = None

        self._ext_folder = FolderExt(self)
        self._ext_host = HostExt(self)
        self._ext_vm = VmExt(self)

        return
    
    @property
    def Folder(self) -> FolderExt:
        return self._ext_folder

    @property
    def Host(self) -> HostExt:
        return self._ext_host

    @property
    def Vm(self) -> VmExt:
        return self._ext_vm

    def build_api_url(self, leaf: str):

        url = self._api_root + leaf
        
        return url

    def renew_session(self):
        
        req_url = f"{self._rest_root}/com/vmware/cis/session"

        resp = self._session.post(req_url, auth=(self._credential.username, self._credential.password))
        if resp.status_code == HTTPStatus.OK:
            rcontent = resp.json()
            self._auth_token = rcontent["value"]
            self._session.headers['vmware-api-session-id'] = self._auth_token
        else:
            resp.raise_for_status()
        
        return
    
    def session_delete(self, url: str, **kwargs):

        resp = self._session.delete(url, **kwargs)

        return resp

    def session_get(self, url: str, **kwargs):

        resp = self._session.get(url, **kwargs)

        return resp

    def session_post(self, url: str, data=None, json=None, **kwargs):

        resp = self._session.post(url, data=data, json=None, **kwargs)

        return resp
    
    def session_put(self, url: str, data=None, json=None, **kwargs):

        resp = self._session.put(url, data=data, **kwargs)

        return resp

    
if __name__ == "__main__":

    cred = BasicCredential(identifier='vmuser', categories=['basic'], username='vmuser', password='Virtual11!!')

    agent = VSphereAgent('https://localhost', cred, port=8697)

    vm_list = agent.VM.list()

    print(vm_list)
