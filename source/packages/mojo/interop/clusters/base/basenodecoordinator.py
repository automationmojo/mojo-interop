"""
.. module:: basenodecoordinator
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the BaseNodePoolCoordinator which is used for managing connectivity with pools of OSX capable devices

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

from typing import Any, Dict, List, Optional, Tuple, Union, TYPE_CHECKING

import os
import pprint
import socket
import weakref

from mojo.xmods.exceptions import ConfigurationError
from mojo.xmods.landscaping.friendlyidentifier import FriendlyIdentifier

from mojo.xmods.landscaping.coordinators.coordinatorbase import CoordinatorBase
from mojo.xmods.landscaping.landscapeparameters import LandscapeActivationParams
from mojo.xmods.landscaping.landscapedevice import LandscapeDevice

from mojo.interop.clusters.base.basenode import BaseNode

from mojo.interop.protocols.ssh.sshagent import SshAgent

if TYPE_CHECKING:
    from mojo.xmods.landscaping.landscape import Landscape


def format_node_configuration_error(message, osxdev_config):
    """
        Takes an error message and an node configuration info dictionary and
        formats a configuration error message.
    """
    error_lines = [
        message,
        "DEVICE:"
    ]

    dev_repr_lines = pprint.pformat(osxdev_config, indent=4).splitlines(False)
    for dline in dev_repr_lines:
        error_lines.append("    " + dline)
    
    errmsg = os.linesep.join(error_lines)
    return errmsg

class BaseNodeCoordinator(CoordinatorBase):
    """
        The :class:`BaseNodePoolCoordinator` creates a pool of agents that can be used to
        coordinate the interop activities of the automation process and remote OSX
        node.
    """
    # pylint: disable=attribute-defined-outside-init

    INTEGRATION_CLASS = ""
    CLIENT_TYPE = BaseNode

    def __init__(self, lscape: "Landscape", *args, **kwargs):
        super().__init__(lscape, *args, **kwargs)

        self._cl_upnp_hint_to_ip_lookup: Dict[str, str] = {}
        self._cl_ip_to_host_lookup: Dict[str, str] = {}
        return

    def activate(self, activation_params: LandscapeActivationParams):
        """
            Called by the :class:`LandscapeOperationalLayer` in order for the coordinator to be able to
            potentially enhanced devices.
        """
        return

    def create_landscape_device(self, landscape: "Landscape", device_info: Dict[str, Any]) -> Tuple[FriendlyIdentifier, BaseNode]:
        """
            Called to declare a declared landscape device for a given coordinator.
        """
        host = device_info["host"]
        dev_type = device_info["deviceType"]
        fid = FriendlyIdentifier(host, host)

        device = self.CLIENT_TYPE(landscape, self, fid, dev_type, device_info)
        
        coord_ref = weakref.ref(self)
        device_ref = weakref.ref(device)

        ssh_agent = SshAgent(host, device.ssh_credential)
        ssh_agent.initialize(coord_ref, device_ref, host, host, device_info)

        with self.begin_locked_coordinator_scope() as locked:
            self._cl_children[host] = ssh_agent
            self._cl_ip_to_host_lookup[ssh_agent.ipaddr] = host

        device.attach_extension("network/ssh", ssh_agent)

        return fid, device

    def establish_connectivity(self, activation_params: LandscapeActivationParams):
        """
            Called by the :class:`LandscapeOperationalLayer` in order for the coordinator to be able to
            verify connectivity with devices.
        """
        results = []

        cmd: str = "echo 'It Works'"

        for agent in self.children_as_extension:
            host = agent.host
            ipaddr = agent.ipaddr
            try:
                status, stdout, stderr = agent.run_cmd(cmd)
                results.append((host, ipaddr, status, stdout, stderr, None))
            except Exception as xcpt: # pylint: disable=broad-except
                results.append((host, ipaddr, None, None, None, xcpt))

        return results

    def extend_devices(self, osxdevices: List[LandscapeDevice], upnp_coord: Optional[CoordinatorBase]=None):
        """
            Processes a list of device configs and creates and registers devices and OSX nodes along with
            a SSH node device extensions attached with the landscape for the devices not already registered.

            :param osxdevices: A list of osx device configuration dictionaries.
        """

        lscape: "Landscape" = self.landscape

        dev_config_errors = []

        dev_devices_available = []
        dev_devices_unavailable = []

        for next_dev in osxdevices:
            osxdev_config = next_dev.device_config
            ssh_credential_list = next_dev.ssh_credentials
            if len(ssh_credential_list) == 0:
                errmsg = format_node_configuration_error(
                        "All OSX node devices must have at least one valid credential.", osxdev_config)
                raise ConfigurationError(errmsg) from None

            ssh_cred_by_role = {}
            for ssh_cred in ssh_credential_list:
                cred_role = ssh_cred.role
                if cred_role not in ssh_cred_by_role:
                    ssh_cred_by_role[cred_role] = ssh_cred
                else:
                    errmsg = format_node_configuration_error(
                        "The node device had more than one credentials with the role '{}'".format(cred_role), osxdev_config)
                    raise ConfigurationError(errmsg) from None

            if "priv" not in ssh_cred_by_role:
                errmsg = format_node_configuration_error(
                        "All node devices must have a 'priv' credential.", osxdev_config)
                raise ConfigurationError(errmsg) from None

            priv_cred = ssh_cred_by_role["priv"]

            dev_type = osxdev_config["deviceType"]

            host = None
            upnp_hint = None
            if "host" in osxdev_config:
                host = osxdev_config["host"]
            else:
                pass

            if host is not None:
                called_id = next_dev.identity
                ip = socket.gethostbyname(host)
                self._cl_ip_to_host_lookup[ip] = host

                agent = SshAgent(host, priv_cred, users=ssh_cred_by_role, called_id=called_id)

                osxdev_config["ipaddr"] = agent.ipaddr
                try:
                    status, stdout, stderr = agent.run_cmd("echo Hello")
                    if status == 0 and stdout.strip() == "Hello":
                        dev_devices_available.append(osxdev_config)
                    else:
                        dev_devices_unavailable.append(osxdev_config)
                except:
                    dev_devices_unavailable.append(osxdev_config)

                self._cl_children[host] = agent

                coord_ref = weakref.ref(self)

                fdid = FriendlyIdentifier(host, host)
                basedevice = lscape.create_landscape_device(fdid, dev_type, osxdev_config)
                basedevice = lscape._enhance_landscape_device(basedevice, agent)
                basedevice.initialize_features()

                basedevice.attach_extension("ssh", agent)

                basedevice_ref = weakref.ref(basedevice)
                agent.initialize(coord_ref, basedevice_ref, host, ip, osxdev_config)

                # If this device does not have a USN or hint then it is not a UPNP device so the
                # BaseNodePoolCoordinator is repsonsible for activating it
                if upnp_hint is None:
                    lscape._internal_activate_device(host)

            else:
                dev_config_errors.append(osxdev_config)

        self._available_devices = dev_devices_available
        self._unavailable_devices = dev_devices_unavailable

        return dev_config_errors, dev_devices_available, dev_devices_unavailable

    def lookup_device_by_host(self, host: str) -> Union[LandscapeDevice, None]:
        """
            Looks up the agent for a device by its hostname.  If the
            agent is not found then the API returns None.

            :param host: The host name of the LandscapeDevice to search for.

            :returns: The found LandscapeDevice or None
        """
        device = None

        self._coord_lock.acquire()
        try:
            if host in self._cl_children:
                device = self._cl_children[host].basedevice
        finally:
            self._coord_lock.release()

        return device

    def lookup_device_by_ip(self, ip) -> Union[LandscapeDevice, None]:
        """
            Looks up the agent for a device by its ip address.  If the
            agent is not found then the API returns None.

            :param ip: The ip address of the LandscapeDevice to search for.

            :returns: The found LandscapeDevice or None
        """
        device = None

        self._coord_lock.acquire()
        try:
            if ip in self._cl_ip_to_host_lookup:
                if ip in self._cl_ip_to_host_lookup:
                    host = self._cl_ip_to_host_lookup[ip]
                    if host in self._cl_children:
                        device = self._cl_children[host].basedevice
        finally:
            self._coord_lock.release()

        return device

    def verify_connectivity(self, cmd: str = "echo 'It Works'", user: Optional[str] = None, raiseerror: bool = True) -> List[tuple]:
        """
            Loops through the nodes in the node pool and utilizes the credentials for the specified user in order to verify
            connectivity with the remote node.

            :param cmd: A command to run on the remote machine in order
                        to verify that osx connectivity can be establish.
            :param user: The name of the user credentials to use for connectivity.
                         If the 'user' parameter is not provided, then the
                         credentials of the default or priviledged user will be used.
            :param raiseerror: A boolean value indicating if this API should raise an Exception on failure.

            :returns: A list of errors encountered when verifying connectivity with the devices managed or watched by the coordinator.
        """
        results = []

        for agent in self.children_as_extension:
            host = agent.host
            ipaddr = agent.ipaddr
            try:
                status, stdout, stderr = agent.run_cmd(cmd)
                results.append((host, ipaddr, status, stdout, stderr, None))
            except Exception as xcpt: # pylint: disable=broad-except
                if raiseerror:
                    raise
                results.append((host, ipaddr, None, None, None, xcpt))

        return results
