"""
.. module:: vmworkstationagent
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the VmWorkstationAgen object used to interoperate with VMWare Workstation.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []



from typing import Optional

import base64
from  http import HTTPStatus

from mojo.credentials.basiccredential import BasicCredential

import requests

class VmWorkstationAgent:

    def __init__(self, host: str, credential: BasicCredential, port: Optional[int]=None, verify_certificates: bool=False):
        self._session = requests.session()
        self._session.verify = False

        self._host = host
        self._credential = credential
        self._port = port
        self._verify_certificates = verify_certificates

        self._host_url = self._host.rstrip("/")
        if self._port is not None:
            self._host_url = self._host_url + f":{port}"

        self._api_root_url = self._host_url + "/api/vcenter" 

        self._token = base64.b64encode(f"{credential.username}:{credential.password}".encode("utf8")).decode('utf8')

        return
    
    def vms_list(self):

        headers = {
            'Accept': 'application/vnd.vmware.vmw.rest-v1+json',
            'Authorization': f'Basic {self._token}'
        }

        req_url = f"{self._api_root_url}/vms"

        resp = requests.get(req_url, headers=headers, verify=self._verify_certificates)

        vm_list = None

        if resp.status_code == HTTPStatus.OK:
            vm_list = resp.json()
        else:
            resp.raise_for_status()
        
        return vm_list
    

if __name__ == "__main__":

    cred = BasicCredential(identifier='vmuser', categories=['basic'], username='vmuser', password='Virtual11!!')

    agent = VmWorkstationAgent('https://localhost', cred, port=8697)

    vm_list = agent.vms_list()

    print(vm_list)
