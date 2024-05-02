"""
.. module:: folderext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the FolderExt object.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []


from typing import List, Optional, TYPE_CHECKING

from  http import HTTPStatus

from mojo.interop.services.vmware.datastructures.vcenter import (
    DatacenterSummary, FolderSummary
)

from mojo.interop.services.vmware.vsphere.ext.baseext import BaseExt

if TYPE_CHECKING:
    from mojo.interop.services.vmware.vsphere.vsphereagent import VSphereAgent

class FolderExt(BaseExt):

    def __init__(self, agent: "VSphereAgent"):
        super().__init__(agent)
        return
    
    def find_descendant(self, folder_leaf_names: List[str]):

        agent = self.agent

        search_leaves = [lf for lf in folder_leaf_names]

        filter_datacenters = [agent.filter_state.working_datacenter]

        found = None
        nxtfound = None

        parentFolders = []
        while True:
            nxtleaf = folder_leaf_names.pop(0)

            folders = self.list(datacenters=filter_datacenters, parentfolders=parentFolders)
            for fitem in folders:
                if fitem.name == nxtleaf:
                    nxtfound = fitem
                    break

            if len(folder_leaf_names) > 0:
                parentFolders = [nxtfound]
            else:
                found = nxtfound
                break
    
        return found

    def list(self, *, datacenters: Optional[List[DatacenterSummary]]=None, parentfolders: Optional[List[FolderSummary]]=None) -> List[FolderSummary]:
        folder_list = None

        agent = self.agent

        req_url = agent.build_api_url("/vcenter/folder")

        params = {}
        if datacenters is not None:
            filter_datacenters = [ dc.datacenter for dc in datacenters]
            params['datacenters'] = filter_datacenters
        elif agent.filter_state.has_working_datacenter_filter:
            filter_datacenters = [agent.filter_state.working_datacenter.datacenter]
            params['datacenters'] = filter_datacenters

        if parentfolders is not None:
            filter_parent_folders = [ pf.folder for pf in parentfolders ]
            params['parent_folders'] = filter_parent_folders
        elif agent.filter_state.has_working_folder_filter:
            filter_parent_folders = [ agent.filter_state.working_folder.folder ]
            params['parent_folders'] = filter_parent_folders

        resp = agent.session_get(req_url, params=params)

        if resp.status_code == HTTPStatus.OK:
            found_list = resp.json()

            folder_list = [FolderSummary(**fitem) for fitem in found_list]
        else:
            resp.raise_for_status()

        return folder_list
