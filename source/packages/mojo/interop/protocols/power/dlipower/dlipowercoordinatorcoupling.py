"""
.. module:: powercoordinatorcoupling
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains a PowerCoordinatorCoupling object to use for working with standard
               power agent types.

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

from typing import Any, Dict, List, Tuple, TYPE_CHECKING

from mojo.errors.exceptions import SemanticError
from mojo.xmods.landscaping.coupling.coordinatorcoupling import CoordinatorCoupling
from mojo.xmods.landscaping.friendlyidentifier import FriendlyIdentifier
from mojo.xmods.landscaping.landscape import LandscapeDevice
from mojo.interop.protocols.ssh.sshcoordinator import SshCoordinator

from mojo.xmods.landscaping.constants import StartupLevel

# Types imported only for type checking purposes
if TYPE_CHECKING:
    from mojo.xmods.landscaping.landscape import Landscape

SUPPORTED_INTEGRATION_CLASS = "network/dlipower"

def is_dlipower_type(config_info) -> bool:
    is_sst = False

    if "powerType" in config_info:
        stval = config_info["powerType"]
        if stval == SUPPORTED_INTEGRATION_CLASS:
            is_sst = True

    return is_sst

class PowerCoordinatorCoupling(CoordinatorCoupling):
    """
        The PowerCoordinatorCoupling handle the requirement registration for the SSH coordinator.
    """

    integration_root: str = "apod"
    integration_section: str = "power"
    integration_leaf: str = "powerType"
    integration_class: str = SUPPORTED_INTEGRATION_CLASS

    def __init__(self, *args, **kwargs):
        """
            The default contructor for an :class:`PowerCoordinatorIntegration`.
        """
        super().__init__(*args, **kwargs)
        return

    @classmethod
    def attach_to_environment(cls, landscape: "Landscape"):
        """
            This API is called so that the IntegrationCoupling can process configuration information.  The :class:`IntegrationCoupling`
            will verify that it has a valid environment and configuration to run in.

            :raises :class:`mojo.xmods.exceptions.ConfigurationError`:
        """

        cls.landscape = landscape
        layer_config = landscape.layer_configuration

        power_list = layer_config.get_serial_configs()
        if len(power_list) > 0:
            supported_power_list = [pconf for pconf in filter(is_dlipower_type, power_list)]

            if len(supported_power_list) > 0:
                layer_integ = landscape.layer_integration
                layer_integ.register_integration_dependency(cls)

        return

    @classmethod
    def collect_resources(cls):
        """
            This API is called so the `IntegrationCoupling` can connect with a resource management
            system and gain access to the resources required for the automation run.

            :raises :class:`mojo.xmods.exceptions.ResourceError`:
        """
        return

    @classmethod
    def create_coordinator(cls, landscape: "Landscape") -> object:
        """
            This API is called so that the landscape can create a coordinator for a given integration role.
        """
        cls.coordinator = SshCoordinator(landscape)
        return cls.coordinator

    @classmethod
    def declare_precedence(cls) -> int:
        """
            This API is called so that the IntegrationCoupling can declare an ordinal precedence that should be
            utilized for bringing up its integration state.
        """
        return StartupLevel.Power

    @classmethod
    def diagnostic(cls, label: str, level: int, diag_folder: str):
        """
            The API is called by the :class:`akit.sequencer.Sequencer` object when the automation sequencer is
            building out a diagnostic package at a diagnostic point in the automation sequence.  Example diagnostic
            points are:

            * pre-run
            * post-run

            Each diagnostic package has its own storage location so derived :class:`akit.scope.ScopeCoupling` objects
            can simply write to their specified output folder.

            :param label: The label associated with this diagnostic.
            :param level: The maximum diagnostic level to run dianostics for.
            :param diag_folder: The output folder path where the diagnostic information should be written.
        """
        return

    @classmethod
    def establish_connectivity(cls, allow_missing_devices: bool=False) -> Tuple[List[str], dict]:
        """
            This API is called so the `IntegrationCoupling` can establish connectivity with any compute or storage
            resources.

            :returns: A tuple with a list of error messages for failed connections and dict of connectivity
                      reports for devices devices based on the coordinator.
        """

        config_errors = [], scan_results = {}

        return config_errors, scan_results

    @classmethod
    def establish_presence(cls) -> Tuple[List[str], dict]:
        """
            This API is called so the `IntegrationCoupling` can establish presence with any compute or storage
            resources.

            :returns: A tuple with a list of error messages for failed connections and dict of connectivity
                      reports for devices devices based on the coordinator.
        """
        return

    @classmethod
    def validate_item_configuration(cls, item_info: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """
            Validate the item configuration.
        """
        errors = []
        warnings = []
        
        if "host" not in item_info:
            errmsg = "Serial configuration 'network/dlipower' must have a 'host' field."
            errors.append(errmsg)

        if "port" not in item_info:
            warnmsg = "Device configuration 'network/dlipower' should have a 'port' field."
            warnings.append(warnmsg)

        return errors, warnings

