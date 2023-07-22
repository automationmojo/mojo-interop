"""
.. module:: folderext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the FolderExt object.

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

from typing import List, Optional, TYPE_CHECKING

from  http import HTTPStatus

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

        filter_datacenters = agent.filter_state.datacenters

        found = None
        nxtfound = None

        parentFolders = []
        while True:
            nxtleaf = folder_leaf_names.pop(0)

            folders = self.list(datacenters=filter_datacenters, parentfolders=parentFolders)
            for fitem in folders:
                if fitem["name"] == nxtleaf:
                    nxtfound = fitem
                    break

            if len(folder_leaf_names) > 0:
                parentFolders = [nxtfound["folder"]]
            else:
                found = nxtfound
                break
    
        return found

    def list(self, *, datacenters: Optional[List[str]]=None, parentfolders: Optional[List[str]]=None):
        folder_list = None

        agent = self.agent

        req_url = agent.build_api_url("/vcenter/folder")

        params = {}
        if datacenters is not None:
            params['datacenters'] = datacenters
        elif agent.filter_state.has_datacenter_filters:
            params['datacenters'] = agent.filter_state.datacenters

        if parentfolders is not None:
            params['parent_folders'] = parentfolders
        elif agent.filter_state.has_working_folder_filters:
            params['parent_folders'] = [agent.filter_state.working_folder]

        resp = agent.session_get(req_url, params=params)

        if resp.status_code == HTTPStatus.OK:
            folder_list = resp.json()
        else:
            resp.raise_for_status()

        return folder_list
