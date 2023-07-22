"""
.. module:: vsphereagent
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the VSphereAgent object used to inter-operate with a VSphere server.

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

from typing import List, Optional

from  http import HTTPStatus

import requests

from mojo.xmods.credentials.basiccredential import BasicCredential

from mojo.interop.services.vmware.vsphere.ext.certificatemanagementext import CertificateManagementExt
from mojo.interop.services.vmware.vsphere.ext.clusterext import ClusterExt
from mojo.interop.services.vmware.vsphere.ext.computeext import ComputeExt
from mojo.interop.services.vmware.vsphere.ext.contentext import ContentExt
from mojo.interop.services.vmware.vsphere.ext.cryptomanagerext import CryptoManagerExt
from mojo.interop.services.vmware.vsphere.ext.datacenterext import DataCenterExt
from mojo.interop.services.vmware.vsphere.ext.datastoreext import DataStoreExt
from mojo.interop.services.vmware.vsphere.ext.deploymentext import DeploymentExt
from mojo.interop.services.vmware.vsphere.ext.folderext import FolderExt
from mojo.interop.services.vmware.vsphere.ext.guestext import GuestExt
from mojo.interop.services.vmware.vsphere.ext.hostext import HostExt
from mojo.interop.services.vmware.vsphere.ext.hvcext import HvcExt
from mojo.interop.services.vmware.vsphere.ext.identityext import IdentityExt
from mojo.interop.services.vmware.vsphere.ext.inventoryext import InventoryExt
from mojo.interop.services.vmware.vsphere.ext.isoext import IsoExt
from mojo.interop.services.vmware.vsphere.ext.lcmext import LcmExt
from mojo.interop.services.vmware.vsphere.ext.namespacemanagementext import NamespaceManagementExt
from mojo.interop.services.vmware.vsphere.ext.namespacesext import NamespacesExt
from mojo.interop.services.vmware.vsphere.ext.networkext import NetworkExt
from mojo.interop.services.vmware.vsphere.ext.ovfext import OvfExt
from mojo.interop.services.vmware.vsphere.ext.resourcepoolext import ResourcePoolExt
from mojo.interop.services.vmware.vsphere.ext.servicesext import ServicesExt
from mojo.interop.services.vmware.vsphere.ext.storageext import StorageExt
from mojo.interop.services.vmware.vsphere.ext.systemconfigext import SystemConfigExt
from mojo.interop.services.vmware.vsphere.ext.taggingext import TaggingExt
from mojo.interop.services.vmware.vsphere.ext.tokenserviceext import TokenServiceExt
from mojo.interop.services.vmware.vsphere.ext.topologyext import TopologyExt
from mojo.interop.services.vmware.vsphere.ext.trustedinfrastructureext import TrustedInfrastructureExt
from mojo.interop.services.vmware.vsphere.ext.vmext import VmExt


class VSphereFilterState:

    def __init__(self) -> None:
        self._datacenter_record = None
        self._working_folder_record = None
        return
    
    @property
    def datacenters(self):
        rtnval = []

        if self._datacenter_record is not None:
            rtnval = [self._datacenter_record["datacenter"]]
        
        return rtnval

    @property
    def working_folder(self):
        return self._working_folder_record

    def has_datacenter_filters(self):
        rtnval = False
        if self._datacenter_record is not None:
            rtnval = True
        return rtnval
    
    def has_working_folder_filters(self):
        rtnval = False
        if self._working_folder_record is not None:
            rtnval = True
        return rtnval

    def set_datacenter_filter(self, datacenter_record):
        self._datacenter_record = datacenter_record
        return
    
    def set_working_folder_filter(self, working_folder_record):
        self._working_folder_record = working_folder_record
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

        self._ext_certificatemanagement = CertificateManagementExt(self)
        self._ext_cluster = ClusterExt(self)
        self._ext_compute = ComputeExt(self)
        self._ext_content = ContentExt(self)
        self._ext_cryptomanager = CryptoManagerExt(self)
        self._ext_datacenter = DataCenterExt(self)
        self._ext_datastore = DataStoreExt(self)
        self._ext_deployment = DeploymentExt(self)
        self._ext_folder = FolderExt(self)
        self._ext_guest = GuestExt(self)
        self._ext_host = HostExt(self)
        self._ext_hvc = HvcExt(self)
        self._ext_identity = IdentityExt(self)
        self._ext_inventory = InventoryExt(self)
        self._ext_iso = IsoExt(self)
        self._ext_lcm = LcmExt(self)
        self._ext_namespacemanagement = NamespaceManagementExt(self)
        self._ext_namespaces = NamespacesExt(self)
        self._ext_network = NetworkExt(self)
        self._ext_ovf = OvfExt(self)
        self._ext_resourcepool = ResourcePoolExt(self)
        self._ext_services = ServicesExt(self)
        self._ext_storage = StorageExt(self)
        self._ext_systemconfig = SystemConfigExt(self)
        self._ext_tagging = TaggingExt(self)
        self._ext_tokenservice = TokenServiceExt(self)
        self._ext_topology = TopologyExt(self)
        self._ext_trustedinfrastructure = TrustedInfrastructureExt(self)
        self._ext_vm = VmExt(self)

        self._filter_state = VSphereFilterState()

        return
    
    @property
    def filter_state(self) -> VSphereFilterState:
        return self._filter_state

    @property
    def CertificateManagement(self) -> CertificateManagementExt:
        return self._ext_certificatemanagement
    
    @property
    def Cluster(self) -> ClusterExt:
        return self._ext_cluster
    
    @property
    def Compute(self) -> ComputeExt:
        return self._ext_compute
    
    @property
    def Content(self) -> ContentExt:
        return self._ext_content

    @property
    def CryptoManager(self) -> CryptoManagerExt:
        return self._ext_cryptomanager

    @property
    def DataCenter(self) -> DataCenterExt:
        return self._ext_datacenter
    
    @property
    def DataStore(self) -> DataStoreExt:
        return self._ext_datastore
    
    @property
    def Deployment(self) -> DeploymentExt:
        return self._ext_deployment

    @property
    def Folder(self) -> FolderExt:
        return self._ext_folder

    @property
    def Guest(self) -> GuestExt:
        return self._ext_guest

    @property
    def Host(self) -> HostExt:
        return self._ext_host
    
    @property
    def Hvc(self) -> HvcExt:
        return self._ext_hvc
    
    @property
    def Identity(self) -> IdentityExt:
        return self._ext_identity
    
    @property
    def Inventory(self) -> InventoryExt:
        return self._ext_inventory
    
    @property
    def Iso(self) -> IsoExt:
        return self._ext_iso
    
    @property
    def Lcm(self) -> LcmExt:
        return self._ext_lcm
    
    @property
    def NamespaceManagement(self) -> NamespaceManagementExt:
        return self._ext_namespacemanagement
    
    @property
    def Namespaces(self) -> NamespacesExt:
        return self._ext_namespaces

    @property
    def Network(self) -> NetworkExt:
        return self._ext_network
    
    @property
    def ResourcePool(self) -> ResourcePoolExt:
        return self._ext_resourcepool

    @property
    def Services(self) -> ServicesExt:
        return self._ext_services
    
    @property
    def Storage(self) -> StorageExt:
        return self._ext_storage
    
    @property
    def SystemConfig(self) -> SystemConfigExt:
        return self._ext_systemconfig

    @property
    def Tagging(self) -> TaggingExt:
        return self._ext_tagging
    
    @property
    def TokenService(self) -> TokenServiceExt:
        return self._ext_tokenservice

    @property
    def Topology(self) -> TopologyExt:
        return self._ext_topology
    
    @property
    def TrustedInfrastructure(self) -> TrustedInfrastructureExt:
        return self._ext_trustedinfrastructure

    @property
    def Vm(self) -> VmExt:
        return self._ext_vm

    def apply_working_folder_filter(self, container_path: str):

        dcrecord = None
        folderspec = None

        if container_path.find(":") >= 0:
            datacenter, folderspec = container_path.split(":")
            dcrecord = self.DataCenter.get(datacenter)
            self._filter_state.set_datacenter_filter(dcrecord)

        folderspec = folderspec.lstrip("/")
        folder_leafs = folderspec.split("/")

        cont_folder = self.Folder.find_descendant(folder_leafs)
        self._filter_state.set_working_folder_filter(cont_folder)

        return

    def build_api_url(self, leaf: str) -> str:

        url = self._api_root + leaf
        
        return url

    def renew_session(self):
        
        req_url = f"{self._rest_root}/com/vmware/cis/session"

        resp = self._session.post(req_url, auth=(self._credential.username, self._credential.password), verify=False)
        if resp.status_code == HTTPStatus.OK:
            rcontent = resp.json()
            self._auth_token = rcontent["value"]
            self._session.headers['vmware-api-session-id'] = self._auth_token
        else:
            resp.raise_for_status()
        
        return
    
    def session_delete(self, url: str, **kwargs) -> requests.Response:

        resp = self._session.delete(url, **kwargs)

        return resp

    def session_get(self, url: str, **kwargs) -> requests.Response:

        resp = self._session.get(url, **kwargs)

        return resp

    def session_post(self, url: str, data=None, json=None, **kwargs) -> requests.Response:

        resp = self._session.post(url, data=data, json=None, **kwargs)

        return resp
    
    def session_put(self, url: str, data=None, json=None, **kwargs) -> requests.Response:

        resp = self._session.put(url, data=data, **kwargs)

        return resp

    
if __name__ == "__main__":

    cred = BasicCredential(identifier='vmuser', categories=['basic'], username='vmuser', password='Virtual11!!')

    agent = VSphereAgent('https://localhost', cred, port=8697)

    vm_list = agent.VM.list()

    print(vm_list)

