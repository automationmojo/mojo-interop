"""

    NOTE: This is a code generated file.  This file should not be edited directly.
"""



from mojo.interop.protocols.upnp.aspects import AspectsUPnP, DEFAULT_UPNP_ASPECTS

from mojo.xmods.extension.dynamic import DynamicExtension
from mojo.interop.protocols.upnp.services.upnpserviceproxy import UpnpServiceProxy

class CloudProxyDevice1ServiceProxy(UpnpServiceProxy, DynamicExtension):
    """
        This is a code generated proxy class to the 'urn:schemas-upnp-org:service:CloudProxyDevice:1' service.
    """

    SERVICE_MANUFACTURER = 'UPnP'
    SERVICE_TYPE = 'CloudProxyDevice1'

    SERVICE_DEFAULT_VARIABLES = {}

    SERVICE_EVENT_VARIABLES = {}
