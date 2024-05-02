"""
.. module:: sshbase
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`SshBase` class.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>

"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []


from typing import Optional, Sequence, Union, Tuple

import logging
import weakref

import paramiko

from mojo.xmods.aspects import  AspectsCmd, DEFAULT_CMD_ASPECTS
from mojo.credentials.sshcredential import SshCredential
from mojo.landscaping.protocolextension import ProtocolExtension
from mojo.interfaces.isystemcontext import ISystemContext

from mojo.interop.protocols.ssh.sshbase import SshBase
from mojo.interop.protocols.ssh.sshconst import (
    SshJumpParams
)
from mojo.interop.protocols.ssh.sshsession import SshSession


logger = logging.getLogger()


class SshAgent(SshBase, ProtocolExtension):
    """
        The :class:`SshAgent` provides an extension of the :class:`SshBase` class interface and api(s).  The :class:`SshAgent` manages connection
        and interop settings that are used to perform operations and interact with a remote SSH service.  The :class:`SshAgent` provides standard
        APIs for running command and transferring files along with code that helps ensure commands are logged cleanly.  The :class:`SshAgent` also
        provides run patterning to help eliminate duplication of code associated with running SSH commands in loops.
    """
    def __init__(self, host: str, primary_credential: SshCredential, users: Optional[dict] = None, port: int = 22, jump: Union[str, SshJumpParams, None] = None,
                 pty_params: Optional[dict] = None, called_id: Optional[str]=None, look_for_keys: bool = False, aspects: AspectsCmd = DEFAULT_CMD_ASPECTS):
        SshBase.__init__(self, host, primary_credential, users=users, port=port, jump=jump,
                         pty_params=pty_params, called_id=called_id, look_for_keys=look_for_keys, aspects=aspects)
        ProtocolExtension.__init__(self)
        return

    def initialize(self, coord_ref: weakref.ReferenceType, basedevice_ref: weakref.ReferenceType, extid: str, location: str, configinfo: dict):
        """
            Initializes the landscape device extension. It is not required to call this function in order to use an SSHAgent, it is used
            when an agent is attached to a LandscapeDevice as a device extension.

            :param coord_ref: A weak reference to the coordinator that is managing interactions through this
                              device extension.
            :param extid: A unique reference that can be used to identify this device via the coordinator even if its location changes.
            :param location: The location reference where this device can be found via the coordinator.
            :param configinfo: The configuration information dictionary from the landscape file for the specified host.
        """
        ProtocolExtension.initialize(self, coord_ref, basedevice_ref, extid, location, configinfo)
        return

    def open_session(self, primitive: bool = False, pty_params: Optional[dict] = None, interactive=False, basis_session: Optional[SshSession] = None,
                     aspects: Optional[AspectsCmd] = None) -> SshSession:
        """
            Provies a mechanism to create a :class:`SshSession` object with derived settings.  This method allows various parameters for the session
            to be overridden.  This allows for the performing of a series of SSH operations under a particular set of shared settings and or credentials.

            :param primitive: Use primitive mode for FTP operations for the session.
            :param pty_params: The default pty parameters to use to request a PTY when running commands through the session.
            :param interactive: Creates an interactive session which holds open an interactive shell so commands can interact in the shell.
            :param basis_session: An optional SshSession instance to use as a session basis.  This allows re-use of sessions.
            :param aspects: The default run aspects to use for the operations performed by the session.
        """

        if aspects is None:
            aspects = self._aspects

        session = None
        if basis_session is not None:
            bs: SshBase = basis_session
            session = SshSession(bs._host, bs._primary_credential, users=bs._users, port=bs._port,
                                 jump=bs._jump, pty_params=pty_params, interactive=interactive,
                                 basis_session=basis_session, look_for_keys=bs._look_for_keys, aspects=aspects)
        else:
            session = SshSession(self._host, self._primary_credential, users=self._users, port=self._port,
                                 jump=self._jump, pty_params=pty_params, interactive=interactive, look_for_keys=self._look_for_keys, aspects=aspects)
        return session

    def reboot(self, aspects: Optional[AspectsCmd] = None):
        """
            Reboots the designated host by running the 'reboot' command on the host.
            
            ..note: This method is not a typical SSH functionality, but it was added so that
                    automatic reconnects can be implemented as required on session objects.

        """
        reboot_cmd = 'reboot'
        try:
            status, stdout, stderr = self.run_cmd(reboot_cmd, aspects=aspects)
        except:
            # We might see a connection dropout exception here, so we need
            # to handle it.
            pass

        # Since we are NOT a session, we need to verify the remote machine is back up by attempting to
        # connect to the machine and run a command. We raise a TimeoutError if we cannot connect and
        # run a command before the reboot_timeout runs out.
        
        return

    def run_cmd(self, command: str, exp_status: Union[int, Sequence]=0, user: str = None, pty_params: dict = None, aspects: Optional[AspectsCmd] = None, ssh_client: Optional[paramiko.SSHClient]=None) -> Tuple[int, str, str]: # pylint: disable=arguments-differ
        """
            Runs a command on the designated host using the specified parameters.

            :param command: The command to run.
            :param exp_status: An integer or sequence of integers that specify the set of expected status codes from the command.
            :param user: The registered name of the user role to use to lookup the credentials for running the command.
            :param pty_params: The pty parameters to use to request a PTY when running the command.
            :param aspects: The run aspects to use when running the command.
            :param ssh_client: An optional connected SSHClient that should be for the operation.

            :returns: The status, stderr and stdout from the command that was run.
        """
        cleanup_client = False

        status, stdout, stderr = None, None, None

        try:
            if ssh_client is None:
                # If we are not passed in a client to use, we create one
                # and then clean it up before returning
                ssh_client = self._create_client()
                cleanup_client = True

            status, stdout, stderr = self._run_cmd(ssh_client, command, exp_status=exp_status, user=user, pty_params=pty_params, aspects=aspects)

        finally:
            # If we created a client, clean it up
            if cleanup_client:
                ssh_client.close()
                del ssh_client

        return status, stdout, stderr

    def directory_tree(self, root_dir: str, depth: int = 1, ssh_client: Optional[paramiko.SSHClient] = None) -> dict:
        """
            Method that creates a directory tree for the folder.

            :param root_dir: The root directory to scan when creating the tree.
            :param depth: The dept to scan to
            :param ssh_client: An optional connected SSHClient that should be for the operation.

            :returns: A dictionary with a tree of information about the directory tree found on the remote system.
        """
        dir_info = {}

        cleanup_client = False
        try:
            if ssh_client is None:
                ssh_client = self._create_client()
                cleanup_client = True

            dir_info = self._directory_tree(ssh_client, root_dir, depth=depth)

        finally:
            if cleanup_client:
                ssh_client.close()
                del ssh_client

        return dir_info

    def directory(self, root_dir: str, ssh_client: Optional[paramiko.SSHClient] = None) -> dict:
        """
            Method that creates a directory listing for the folder.

            :param root_dir: The directory to scan when creating the tree.
            :param ssh_client: An optional connected SSHClient that should be for the operation.

            :returns: A dictionary that contains information about the items in the target directory.
        """
        dir_info = {}

        cleanup_client = False
        try:
            if ssh_client is None:
                ssh_client = self._create_client()
                cleanup_client = True

            dir_info = self._directory(ssh_client, root_dir)

        finally:
            if cleanup_client:
                ssh_client.close()
                del ssh_client

        return dir_info

    def directory_exists(self, remotedir: str, ssh_client: Optional[paramiko.SSHClient] = None) -> bool:
        """
            Method used to check if a remote directory exists.

            :param remotedir: The remote remotedir path to check for existance.
            :param ssh_client: An optional connected SSHClient that should be for the operation.
        """
        exists = False

        try:
            if ssh_client is None:
                ssh_client = self._create_client()
                cleanup_client = True

            self._directory_exists(ssh_client, remotedir)

        finally:
            if cleanup_client:
                ssh_client.close()
                del ssh_client

        return exists

    def file_exists(self, remotepath: str, ssh_client: Optional[paramiko.SSHClient] = None) -> bool:
        """
            Method used to check if a remote file exists.

            :param remotepath: The remote file path to check for existance.
            :param ssh_client: An optional connected SSHClient that should be for the operation.
        """
        exists = False

        try:
            if ssh_client is None:
                ssh_client = self._create_client()
                cleanup_client = True

            exists = self._file_exists(ssh_client, remotepath)

        finally:
            if cleanup_client:
                ssh_client.close()
                del ssh_client

        return exists

    def file_pull(self, remotepath: str, localpath: str, ssh_client: Optional[paramiko.SSHClient] = None):
        """
            Method used to pull a remote file to a local file path.

            :param remotepath: The remote file path to pull to the local file.
            :param localpath: The local file path to pull the content to.
            :param ssh_client: An optional connected SSHClient that should be for the operation.
        """
        cleanup_client = False
        try:
            if ssh_client is None:
                ssh_client = self._create_client()
                cleanup_client = True

            self._file_pull(ssh_client, remotepath, localpath)

        finally:
            if cleanup_client:
                ssh_client.close()
                del ssh_client

        return

    def file_push(self, localpath: str, remotepath: str, ssh_client: Optional[paramiko.SSHClient] = None):
        """
            Method used to push a local file to a remote file path.

            :param localpath: The local file path to push the content of to the remote file.
            :param remotepath: The remote file path to push content to.
            :param ssh_client: An optional connected SSHClient that should be for the operation.
        """
        cleanup_client = False
        try:
            if ssh_client is None:
                ssh_client = self._create_client()
                cleanup_client = True

            self._file_push(ssh_client, localpath, remotepath)

        finally:
            if cleanup_client:
                ssh_client.close()
                del ssh_client

        return

    def get_home_directory(self, aspects: Optional[AspectsCmd] = None) -> str:
        """
            Method used to get the home directory of the credentialed user from a remote machine.
        """
        home_dir = self._get_home_directory(aspects=aspects)
        return home_dir