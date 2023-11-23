
from mojo.landscaping.service.servicecoordinatorcouplingbase import ServiceCoordinatorCouplingBase

from mojo.interop.services.common import INTEGRATIION_CLASS_FOR_VSPHERE_VCENTER_SERVICE
from mojo.interop.services.vmware.vsphere.vspherecoordinator import VSphereCoordinator

class VSphereCoordinatorCoupling(ServiceCoordinatorCouplingBase):

    integration_class: str = INTEGRATIION_CLASS_FOR_VSPHERE_VCENTER_SERVICE

    COORDINATOR_TYPE = VSphereCoordinator

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        return
