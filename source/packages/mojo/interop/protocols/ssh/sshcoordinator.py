"""
.. module:: sshcoordinator
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the SshPoolCoordinator which is used for managing connectivity with pools of ssh capable devices

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []


from typing import Any, Dict, List, Optional, Tuple, Union, TYPE_CHECKING

import os
import pprint
import weakref

from mojo.landscaping.friendlyidentifier import FriendlyIdentifier

from mojo.landscaping.coordinators.coordinatorbase import CoordinatorBase
from mojo.landscaping.landscapeparameters import LandscapeActivationParams
from mojo.landscaping.landscapedevice import LandscapeDevice

from mojo.interop.protocols.ssh.sshagent import SshAgent
from mojo.interop.protocols.ssh.sshdevice import SshDevice

if TYPE_CHECKING:
    from mojo.landscaping.landscape import Landscape

SUPPORTED_INTEGRATION_CLASS = "network/ssh"

def format_ssh_device_configuration_error(message, sshdev_config):
    """
        Takes an error message and an SSH device configuration info dictionary and
        formats a configuration error message.
    """
    error_lines = [
        message,
        "DEVICE:"
    ]

    dev_repr_lines = pprint.pformat(sshdev_config, indent=4).splitlines(False)
    for dline in dev_repr_lines:
        error_lines.append("    " + dline)
    
    errmsg = os.linesep.join(error_lines)
    return errmsg

class SshCoordinator(CoordinatorBase):
    """
        The :class:`SshPoolCoordinator` creates a pool of agents that can be used to
        coordinate the interop activities of the automation process and remote SSH
        nodes.
    """
    # pylint: disable=attribute-defined-outside-init

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

    def create_landscape_device(self, landscape: "Landscape", device_info: Dict[str, Any]) -> Tuple[FriendlyIdentifier, SshDevice]:
        """
            Called to declare a declared landscape device for a given coordinator.
        """
        host = device_info["host"]
        dev_type = device_info["deviceType"]
        fid = FriendlyIdentifier(host, host)

        device = SshDevice(landscape, self, fid, dev_type, device_info)
        
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
            Loops through the nodes in the SSH pool and utilizes the credentials for the specified user in order to verify
            connectivity with the remote node.

            :param cmd: A command to run on the remote machine in order
                        to verify that ssh connectivity can be establish.
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
