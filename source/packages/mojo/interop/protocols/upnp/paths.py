"""
.. module:: paths
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing constants for different paths utilize by the code generator that are relative to the test framework.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>

"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []



import os

from mojo.collections.context import Context
from mojo.collections.contextpaths import ContextPaths

DIR_UPNP = os.path.dirname(__file__)


DIR_UPNP_EXTENSIONS = os.path.join(DIR_UPNP, "extensions")

DIR_UPNP_EXTENSIONS_STANDARD = os.path.join(DIR_UPNP_EXTENSIONS, "standard")
DIR_UPNP_EXTENSIONS_STANDARD_EMBEDDEDDEVICES = os.path.join(DIR_UPNP_EXTENSIONS_STANDARD, "embeddeddevices")
DIR_UPNP_EXTENSIONS_STANDARD_ROOTDEVICES = os.path.join(DIR_UPNP_EXTENSIONS_STANDARD, "rootdevices")
DIR_UPNP_EXTENSIONS_STANDARD_SERVICES = os.path.join(DIR_UPNP_EXTENSIONS_STANDARD, "services")

DIR_UPNP_GENERATOR = os.path.join(DIR_UPNP, "generator")

DIR_UPNP_GENERATOR_STANDARD = os.path.join(DIR_UPNP_GENERATOR, "standard")
DIR_UPNP_GENERATOR_STANDARD_EMBEDDEDDEVICES = os.path.join(DIR_UPNP_GENERATOR_STANDARD, "embeddeddevices")
DIR_UPNP_GENERATOR_STANDARD_ROOTDEVICES = os.path.join(DIR_UPNP_GENERATOR_STANDARD, "rootdevices")
DIR_UPNP_GENERATOR_STANDARD_SERVICES = os.path.join(DIR_UPNP_GENERATOR_STANDARD, "services")

context = Context()
runtime_home_dir = context.lookup(ContextPaths.RUNTIME_HOME_DIRECTORY, default=os.path.expanduser("~/mjr"))

DIR_UPNP_EXTENSIONS_INTEGRATION = os.path.join(runtime_home_dir, "upnp", "extensions")
upnp_extensions_integration_base = context.lookup("/upnp/extensions/integration/base")
if upnp_extensions_integration_base is not None:
    DIR_UPNP_EXTENSIONS_INTEGRATION = upnp_extensions_integration_base

DIR_UPNP_EXTENSIONS_INTEGRATION_EMBEDDEDDEVICES = os.path.join(DIR_UPNP_EXTENSIONS_INTEGRATION, "embeddeddevices")
DIR_UPNP_EXTENSIONS_INTEGRATION_ROOTDEVICES = os.path.join(DIR_UPNP_EXTENSIONS_INTEGRATION, "rootdevices")
DIR_UPNP_EXTENSIONS_INTEGRATION_SERVICES = os.path.join(DIR_UPNP_EXTENSIONS_INTEGRATION, "services")

DIR_UPNP_SCAN_INTEGRATION = os.path.join(runtime_home_dir, "upnp", "scan")
upnp_scan_integration_base = context.lookup("/upnp/extensions/integration/base")
if upnp_scan_integration_base is not None:
    DIR_UPNP_SCAN_INTEGRATION = upnp_scan_integration_base

DIR_UPNP_SCAN_INTEGRATION_EMBEDDEDDEVICES = os.path.join(DIR_UPNP_SCAN_INTEGRATION, "embeddeddevices")
DIR_UPNP_SCAN_INTEGRATION_ROOTDEVICES = os.path.join(DIR_UPNP_SCAN_INTEGRATION, "rootdevices")
DIR_UPNP_SCAN_INTEGRATION_SERVICES = os.path.join(DIR_UPNP_SCAN_INTEGRATION, "services")
