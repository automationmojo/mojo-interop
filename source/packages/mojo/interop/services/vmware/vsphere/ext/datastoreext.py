"""
.. module:: datastoreext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the DataStoreExt object.

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

class DataStoreExt(BaseExt):

    def __init__(self, agent: "VSphereAgent"):
        super().__init__(agent)
        return
    
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