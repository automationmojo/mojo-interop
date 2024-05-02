"""
.. module:: sshsession
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`SshSession` class.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>

"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []


from typing import Optional, Sequence, Union, Tuple

import logging
import paramiko

from types import TracebackType

from mojo.xmods.aspects import AspectsCmd, DEFAULT_CMD_ASPECTS
from mojo.credentials.sshcredential import SshCredential
from mojo.interfaces.isystemcontext import ISystemContext

from mojo.interop.protocols.ssh.sshconst import (
    SshJumpParams,
    DEFAULT_SSH_TIMEOUT,
    DEFAULT_SSH_RETRY_INTERVAL,
    INTERACTIVE_PROMPT
)
from mojo.interop.protocols.ssh.sshhelpers import (
    ssh_execute_command,
    ssh_execute_command_in_channel
)
from mojo.interop.protocols.ssh.sshbase import SshBase

logger = logging.getLogger()

class SshSession(SshBase):
    """
        The :class:`SshSession` provides an extension of the :class:`SshBase` class interface and api(s).  The :class:`SshSession` serves to
        act as a session scoping object that establishes a set of SSH credentials, settings and patterns that are to be used for a series of
        SSH operations.  The :class:`SshSession` also holds open the SSHClient for its entire scope and ensures the SSHClient is closed and
        cleaned up properly when the :class:`SshSession` goes out of scope.
    """
    def __init__(self, host: str, primary_credential: SshCredential, users: Optional[dict] = None, port:int=22, jump: Union[str, SshJumpParams, None] = None,
                 pty_params: Optional[dict] = None, session_user=None, interactive=False, basis_session: Optional["SshSession"]=None,
                 called_id: Optional[str]=None, look_for_keys: bool = False, aspects: AspectsCmd=DEFAULT_CMD_ASPECTS):
        SshBase.__init__(self, host, primary_credential, users=users, port=port, jump=jump,
                         pty_params=pty_params, called_id=called_id, look_for_keys=look_for_keys, aspects=aspects)

        self._session_user = session_user
        self._interactive = interactive
        self._read_timeout = 2

        self._ssh_client = None
        self._ssh_runner = None
        self._basis_session = basis_session
        return

    def __enter__(self):
        """
            Method that implements the __enter__ symantics used for 'with' statements.
        """
        self._ssh_client = self._create_client()

        if self._interactive:
            inactivity_timeout = self._aspects.inactivity_timeout

            channel = self._ssh_client.get_transport().open_session(timeout=inactivity_timeout)

            if self._pty_params is not None:
                channel.get_pty(**self._pty_params)
            else:
                channel.get_pty()

            channel.invoke_shell()
            channel.sendall("export PS1=%s\n" % INTERACTIVE_PROMPT)

            leader = b""
            try:
                while True:
                    out = channel.in_buffer.read(1028, self._read_timeout)
                    leader += out
            except paramiko.buffered_pipe.PipeTimeout as _:
                # We don't need to do anything if the pipe, times out.
                # it means we are likely at the command prompt and that
                # there is nothing to read.
                pass

            self._ssh_runner = channel
        else:
            self._ssh_runner = self._ssh_client

        return self

    def __exit__(self, ex_type: type, ex_val: Exception, ex_tb: TracebackType) -> bool:
        """
            Method that implements the __exit__ symantics used for 'with' statements.

            :returns: Returns false indicating that exceptions are not handled.
        """
        self.close()
        handled = False
        return handled

    def close(self):
        """
            Closes the SSH session and the assocatied SSH connection.
        """
        # Only close the client if this session owns the client
        if self._basis_session is None:
            self._ssh_client.close()
        return

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

        # Since we are a session, we need to reconnect to the remote machine after the reboot.
        # We raise a TimeoutError if we do not reconnect before the reboot_timeout runs out.
        
        return

    def run_cmd(self, command: str, exp_status: Union[int, Sequence]=0, user: str = None, pty_params: dict = None, aspects: Optional[AspectsCmd] = None) -> Tuple[int, str, str]:
        """
            Runs a command on the designated host using the current session SSH session and client.

            :param command: The command to run.
            :param exp_status: An integer or sequence of integers that specify the set of expected status codes from the command.
            :param user: The registered name of the user role to use to lookup the credentials for running the command.
            :param pty_params: The pty parameters to use to request a PTY when running the command.
            :param aspects: The run aspects to use when running the command.

            :returns: The status, stderr and stdout from the command that was run.
        """

        status, stdout, stderr = self._run_cmd(self._ssh_runner, command, user=user, pty_params=pty_params, aspects=aspects)

        return status, stdout, stderr

    def directory(self, root_dir: str) -> dict:
        """
            Method that creates a directory listing for the folder.

            :param root_dir: The directory to scan when creating the tree.

            :returns: A dictionary that contains information about the items in the target directory.
        """
        dir_info = self._directory(self._ssh_client, root_dir)

        return dir_info

    def directory_exists(self, remotedir: str) -> bool:
        """
            Method used to pull a remote directory to check for existance.

            :param remotedir: The remote directory path to check for existance.

            :returns: A boolean value indicating if the remote file exists.
        """
        exists = self._directory_exists(self._ssh_client, remotedir)

        return exists

    def directory_tree(self, root_dir: str, depth: int = 1) -> dict:
        """
            Method that creates a directory tree for the folder.

            :param root_dir: The root directory to scan when creating the tree.
            :param depth: The dept to scan to

            :returns: A dictionary with a tree of information about the directory tree found on the remote system.
        """
        dir_info = self._directory_tree(self._ssh_client, root_dir, depth=depth)

        return dir_info

    def file_exists(self, remotepath: str) -> bool:
        """
            Method used to pull a remote file to check for existance.

            :param remotepath: The remote file path to check for existance.

            :returns: A boolean value indicating if the remote file exists.
        """
        exists = self._file_exists(self._ssh_client, remotepath)

        return exists

    def file_pull(self, remotepath: str, localpath: str):
        """
            Method used to pull a remote file to a local file path.

            :param remotepath: The remote file path to pull to the local file.
            :param localpath: The local file path to pull the content to.
        """
        self._file_pull(self._ssh_client, remotepath, localpath)

        return

    def file_push(self, localpath: str, remotepath: str):
        """
            Method used to push a local file to a remote file path.

            :param localpath: The local file path to push the content of to the remote file.
            :param remotepath: The remote file path to push content to.
        """
        self._file_push(self._ssh_client, localpath, remotepath)

        return

    def get_home_directory(self, aspects: Optional[AspectsCmd] = None) -> str:
        """
            Method used to get the home directory of the credentialed user from a remote machine.
        """
        home_dir = self._get_home_directory(aspects=aspects)
        return home_dir

    def open_session(self, primitive: bool = False, pty_params: Optional[dict] = None, interactive=False, basis_session: Optional["SshSession"] = None,
                     aspects: Optional[AspectsCmd] = None, **kwargs) -> "SshSession":
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
            bs: SshSession = basis_session
            session = SshSession(bs._host, bs._primary_credential, users=bs._users, port=bs._port,
                                 jump=bs._jump, pty_params=pty_params, interactive=interactive,
                                 basis_session=bs, look_for_keys=bs._look_for_keys, aspects=aspects)
        else:
            session = SshSession(self._host, self._primary_credential, users=self._users, port=self._port,
                                 jump=self._jump, pty_params=pty_params, interactive=interactive,
                                 look_for_keys=self._look_for_keys, aspects=aspects)
        return session

    def _create_client(self, session_user: Optional[str] = None) -> paramiko.SSHClient:
        """
            Create an SSHClient to use for running commands and performing FTP operations.

            :param session_user: The user role and associated credentials to use when creating the SSHClient.

            :returns: An SSHClient object connected to the remote machine under the default or specified user credential.
        """
        ssh_client = None
        if self._basis_session is not None:
            ssh_client = self._basis_session._ssh_client
        else:
            ssh_client = SshBase._create_client(self, session_user=session_user)
        return ssh_client

    def _ssh_execute_command(self, ssh_runner, command: str, pty_params=None, inactivity_timeout: float=DEFAULT_SSH_TIMEOUT, inactivity_interval: float=DEFAULT_SSH_RETRY_INTERVAL, chunk_size: int=1024) -> Tuple[int, str, str]:
        """
            Private helper method used to route the command running parameters to the correct routine based on whether the command is being run interactively
            through a session or is a single run command from an SshAgent.

            :param ssh_runner: A :class:`paramiko.SSHClient` or :class:`paramiko.Channel` object that can be used to run a command on a remote machine.
            :param command: The command that is to be run.
            :param pty_params: A dictionary of parameters that are passed to paramiko to get a pty when running commands.
            :param inactivity_timeout: A timeout for inactivity between the local machine and remote machine.
            :param inactivity_interval: The interval to wait between attempts to interact or read from the remote machine.
            :param chunk_size: The size of the buffer to use when reading results from the remote machine.
        """
        if self._interactive:
            status, stdout, stderr = ssh_execute_command_in_channel(ssh_runner, command, read_timeout=self._read_timeout, inactivity_timeout=inactivity_timeout, inactivity_interval=inactivity_interval)
        else:
            status, stdout, stderr = ssh_execute_command(ssh_runner, command, pty_params=pty_params, inactivity_timeout=inactivity_timeout, inactivity_interval=inactivity_interval)
        return status, stdout, stderr
