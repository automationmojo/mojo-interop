"""
.. module:: hostext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the HostExt object.

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

class HostExt(BaseExt):

    def __init__(self, agent: "VSphereAgent"):
        super().__init__(agent)
        return
    
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