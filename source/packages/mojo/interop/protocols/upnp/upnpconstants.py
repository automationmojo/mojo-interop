__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []
__version__ = "1.0.0"
__maintainer__ = "Myron Walker"
__email__ = "myron.walker@gmail.com"
__status__ = "Development" # Prototype, Development or Production
__license__ = "MIT"

import platform

from mojo.interop.protocols.upnp.aspectsupnp import AspectsUPnP

TIMEDELTA_RENEWAL_WINDOW = 120

UPNP_CALL_COMPLETION_TIMEOUT = 30
UPNP_CALL_COMPLETION_INTERVAL = 5

UPNP_CALL_INACTIVITY_TIMEOUT = 30
UPNP_CALL_INACTIVITY_INTERVAL = 1

DEFAULT_UPNP_CALL_ASPECTS = AspectsUPnP(
    completion_timeout=UPNP_CALL_COMPLETION_TIMEOUT,
    completion_interval=UPNP_CALL_COMPLETION_INTERVAL,
    inactivity_timeout=UPNP_CALL_INACTIVITY_TIMEOUT,
    inactivity_interval=UPNP_CALL_INACTIVITY_INTERVAL)

class UPNP_HEADERS:
    USER_AGENT = "AutomationMojo/1.0 UPNP Test Package"
    SERVER = "{},{},AutomationKit/1.0".format(platform.system(), platform.release())
