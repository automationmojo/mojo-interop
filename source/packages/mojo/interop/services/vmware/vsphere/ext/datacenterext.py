"""
.. module:: datacenterext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the DataCenterExt object.

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

        agent = self.agent
        
        dcinfo = None

        datacenter_list = self.list()
        for dcitem in datacenter_list:
            if dcitem["name"] == name:
                dcinfo = dcitem
                break

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
