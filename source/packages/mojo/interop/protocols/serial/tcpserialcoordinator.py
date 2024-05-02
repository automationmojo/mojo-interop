"""
.. module:: tcpserialcoordinator
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the TcpSerialCoordinator which is used for managing connectivity with pools of tcp serial devices

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []


from typing import Any, Dict, Tuple, Union, TYPE_CHECKING

import weakref

from mojo.landscaping.coordinators.coordinatorbase import CoordinatorBase
from mojo.landscaping.friendlyidentifier import FriendlyIdentifier
from mojo.landscaping.landscapeparameters import LandscapeActivationParams
from mojo.landscaping.landscapedevice import LandscapeDevice

from mojo.interop.protocols.serial.tcpserialagent import TcpSerialAgent

if TYPE_CHECKING:
    from mojo.landscaping.landscape import Landscape

SUPPORTED_INTEGRATION_CLASS = "network/ssh"


class TcpSerialCoordinator(CoordinatorBase):
    """
        The :class:`TcpSerialCoordinator` creates a pool of agents that can be used to
        coordinate the interop activities of the automation process and remote SSH
        nodes.
    """
    # pylint: disable=attribute-defined-outside-init

    def __init__(self, lscape: "Landscape", *args, **kwargs):
        super().__init__(lscape, *args, **kwargs)
        return

    def activate(self, activation_params: LandscapeActivationParams):
        """
            Called by the :class:`LandscapeOperationalLayer` in order for the coordinator to be able to
            potentially enhanced devices.
        """
        return

    def create_landscape_device(self, landscape: "Landscape", device_info: Dict[str, Any]) -> Tuple[FriendlyIdentifier, TcpSerialAgent]:
        """
            Called to declare a declared landscape device for a given coordinator.
        """
        host = device_info["host"]
        port = device_info["port"]
        dev_type = device_info["deviceType"]
        fid = FriendlyIdentifier(host, host)

        device = TcpSerialAgent(landscape, self, fid, dev_type, device_info)
        
        coord_ref = weakref.ref(self)
        device_ref = weakref.ref(device)

        ssh_agent = TcpSerialAgent(host, port=port)
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
