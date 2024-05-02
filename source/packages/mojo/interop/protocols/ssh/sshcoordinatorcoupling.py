"""
.. module:: sshcoordinatorcoupling
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains a SshCoordinatorCoupling object to use for working with the computer nodes via SSH

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []


from typing import Any, Dict, List, Tuple, TYPE_CHECKING

from mojo.landscaping.coupling.coordinatorcoupling import CoordinatorCoupling
from mojo.interop.protocols.ssh.sshcoordinator import SshCoordinator

from mojo.landscaping.constants import StartupLevel

# Types imported only for type checking purposes
if TYPE_CHECKING:
    from mojo.landscaping.landscape import Landscape

SUPPORTED_INTEGRATION_CLASS = "network/ssh"

def is_ssh_device_config(device_info):
    is_ssh_dev = False

    dev_type = device_info["deviceType"]
    if dev_type == SUPPORTED_INTEGRATION_CLASS:
        is_ssh_dev = True

    return is_ssh_dev

class SshCoordinatorCoupling(CoordinatorCoupling):
    """
        The SshCoordinatorCoupling handle the requirement registration for the SSH coordinator.
    """

    pathbase = "/ssh"

    integration_root: str = "apod"
    integration_section: str = "devices"
    integration_leaf: str = "deviceType"
    integration_class: str = SUPPORTED_INTEGRATION_CLASS

    def __init__(self, *args, **kwargs):
        """
            The default contructor for an :class:`SshPoolCoordinatorIntegration`.
        """
        super().__init__(*args, **kwargs)
        return

    @classmethod
    def attach_to_environment(cls, landscape: "Landscape"):
        """
            This API is called so that the IntegrationCoupling can process configuration information.  The :class:`IntegrationCoupling`
            will verify that it has a valid environment and configuration to run in.

            :raises :class:`mojo.xmods.exceptions.AKitMissingConfigError`, :class:`mojo.xmods.exceptions.ConfigurationError`:
        """

        cls.landscape = landscape
        layer_config = landscape.layer_configuration

        device_list = layer_config.get_device_configs()
        if len(device_list) > 0:
            ssh_device_list = [dev for dev in filter(is_ssh_device_config, device_list)]

            if len(ssh_device_list) > 0:
                layer_integ = landscape.layer_integration
                layer_integ.register_integration_dependency(cls)

        return

    @classmethod
    def collect_resources(cls):
        """
            This API is called so the `IntegrationCoupling` can connect with a resource management
            system and gain access to the resources required for the automation run.

            :raises :class:`mojo.xmods.exceptions.AKitResourceError`:
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
        # Because SSH is a protocol that can be used by other coordinators as well, we are considered a
        # secondary protocol.  That is because the SSH coordinator may be called on to add an extension
        # to devices that it did not create and so does not own such as a UPNP device.
        return StartupLevel.SecondaryProtocol

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

            -   deviceType: network/ssh
                name: raspey03
                host: 172.16.1.33
                credentials:
                -    pi-cluster
                features:
                    isolation: false
                skip: false
        """
        errors = []
        warnings = []
        
        if "host" not in item_info:
            errmsg = "Device configuration 'network/ssh' must have a 'host' field."
            errors.append(errmsg)

        if "credentials" not in item_info:
            warnmsg = "Device configuration 'network/ssh' should have a 'credentials' field."
            warnings.append(warnmsg)

        return errors, warnings