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
import os
import socket
import stat
import threading
import time

from datetime import datetime, timedelta
from io import StringIO

import paramiko

from mojo.waiting.waitmodel import TimeoutContext

from mojo.errors.exceptions import ConfigurationError, NotOverloadedError, SemanticError

from mojo.xmods.aspects import ActionPattern, AspectsCmd, LoggingPattern, DEFAULT_CMD_ASPECTS
from mojo.credentials.sshcredential import SshCredential
from mojo.interfaces.isystemcontext import ISystemContext
from mojo.xmods.xformatting import indent_lines
from mojo.xmods.xlogging.scopemonitoring import MonitoredScope

from mojo.interop.protocols.ssh.sshconst import (
    SshJumpParams,
    DEFAULT_SSH_TIMEOUT,
    DEFAULT_SSH_RETRY_INTERVAL,
    TEMPLATE_COMMAND_FAILURE,
    TEMPLATE_COMMAND_SUCCESS
)
from mojo.interop.protocols.ssh.sshhelpers import (
    primitive_directory_exists,
    primitive_file_exists,
    primitive_file_pull,
    primitive_file_push,
    primitive_list_directory,
    primitive_list_tree,
    sftp_list_directory,
    sftp_list_tree,
    ssh_execute_command
)

logger = logging.getLogger()


class SshBase(ISystemContext):
    """
        The :class:`SshBase` object provides for the sharing of state and fuctional patterns
        for APIs between the :class:`SshSession` object and the :class:`SshAgent`.
    """
    def __init__(self, host: str, primary_credential: SshCredential, users: Optional[dict] = None,
                 port: int = 22, jump: Union[str, SshJumpParams, None] = None, pty_params: Optional[dict] = None,
                 called_id: Optional[str]=None, look_for_keys: bool = False,
                 aspects: AspectsCmd = DEFAULT_CMD_ASPECTS):

        self._host = host

        self._primary_credential = primary_credential
        self._username = primary_credential.username
        self._password = primary_credential.password
        self._keyfile = None
        if hasattr(primary_credential, "keyfile"):
            self._keyfile = primary_credential.keyfile
        self._keyraw = None
        if hasattr(primary_credential, "keyraw"):
            self._keyraw = primary_credential.keyraw
        self._keypasswd = None
        if hasattr(primary_credential, "keypasswd"):
            self._keypasswd = primary_credential.keypasswd
        self._allow_agent = None
        if hasattr(primary_credential, "allow_agent"):
            self._allow_agent = primary_credential.allow_agent
        self._primitive = None
        if hasattr(primary_credential, "primitive"):
            self._primitive = primary_credential.primitive

        self._users = users
        self._port = port
        self._jump = jump
        self._pty_params = pty_params
        self._called_id = called_id

        self._target_tag = host
        if self._called_id is not None:
            self._target_tag = "[{}]".format(called_id)
        
        self._look_for_keys = look_for_keys
        self._aspects = aspects

        self._ipaddr = socket.gethostbyname(self._host)

        self._user_lookup_table = {}
        self._group_lookup_table = {}

        if self._password is None and self._keyfile is None and not self._allow_agent:
            raise ConfigurationError("SshAgent requires either a 'password', an identity 'keyfile' or allow_agent=True be specified.") from None
        return

    @property
    def aspects(self) -> AspectsCmd:
        """
            The logging, iteration and other aspects that have been assigned to be used with interacting with the remote SSH service.
        """
        return self._aspects

    @property
    def host(self) -> str:
        """
            The target SSH host machine.
        """
        return self._host

    @property
    def ipaddr(self) -> str:
        """
            The IP address that was found to be associated with the specified host machine.
        """
        return self._ipaddr

    @property
    def jump(self):
        """
            A 'ProxyCommand' jump command that can be used for Advanced Server Access.
        """
        return self._jump
    
    @property
    def look_for_keys(self):
        """
            A value indicating if paramiko should search for keys.
        """
        return self._look_for_keys

    @property
    def port(self) -> int:
        """
            The port to use for SSH communications.  The default is 22.
        """
        return self._port

    @property
    def primary_credential(self):
        """
            Returns the 'primary' user credential provided for this ssh client object.
        """
        return self._primary_credential

    @property
    def pty_params(self) -> dict:
        """
            A dictionary of parameters that are to be passed when getting a PTY when interacting with the remote SSH server.
        """
        return self._pty_params

    @property
    def users(self) -> dict:
        """
            A dictionary of roles and user credentials that can be used for interaction with the remote SSH server.
        """
        return self._users

    def lookup_user_by_uid(self, uid: int, update: bool = True) -> Union[dict, None]:
        """
            A helper method used to lookup cached user information by uid.

            :param uid: The uid of a user.
            :param update: A boolean indicating that the table should be updated if the uid is not found.
        """
        username = None

        if uid in self._user_lookup_table:
            username = self._user_lookup_table[uid]
        elif update:
            status, stdout, _ = self.run_cmd("id -n -u %d" % uid)
            if status == 0:
                username = stdout.strip()
                self._user_lookup_table[uid] = username

        return username

    def lookup_group_by_uid(self, gid: int, update: bool = True) -> Union[dict, None]:
        """
            A helper method used to lookup cached group information by uid.

            :param gid: The gid of a group.
            :param update: A boolean indicating that the table should be updated if the uid is not found.

            :returns: The name of the group associated with the group id or None.
        """
        grpname = None

        if gid in self._group_lookup_table:
            grpname = self._group_lookup_table[gid]
        elif update:
            status, stdout, _ = self.run_cmd("id -n -g %d" % gid)
            if status == 0:
                grpname = stdout.strip()
                self._group_lookup_table[gid] = grpname

        return grpname

    def reboot(self, aspects: Optional[AspectsCmd] = None):
        """
            Reboots the designated host by running the 'reboot' command on the host.
            
            ..note: This method is not a typical SSH functionality, but it was added so that
                    automatic reconnects can be implemented as required on session objects.

        """
        raise NotOverloadedError("SshBase.reboot must be overloaded by derived class '%s'." % type(self).__name__) from None
        reboot_cmd = 'reboot'
        try:
            status, stdout, stderr = self.run_cmd(reboot_cmd, aspects=aspects)
        except:
            # We might see a connection dropout exception here, so we need
            # to handle it.
            pass

        # Try to reconnect to the remote machine after the reboot.  We raise a TimeoutError
        # if we do not reconnect before the reboot_timeout runs out.
        
        return

    def run_cmd(self, command: str, exp_status: Union[int, Sequence]=0, user: str = None, pty_params: dict = None, aspects: Optional[AspectsCmd] = None) -> Tuple[int, str, str]:
        """
            Runs a command on the designated host using the specified parameters.

            :param command: The command to run.
            :param exp_status: An integer or sequence of integers that specify the set of expected status codes from the command.
            :param user: The registered name of the user role to use to lookup the credentials for running the command.
            :param pty_params: The pty parameters to use to request a PTY when running the command.
            :param aspects: The run aspects to use when running the command.

            :returns: The status, stderr and stdout from the command that was run.
        """
        raise NotOverloadedError("SshBase.run_cmd must be overloaded by derived class '%s'." % type(self).__name__) from None

    def verify_connectivity(self) -> bool:
        """
            Method that can be used to verify connectivity to the target computer.

            :returns: A boolean value indicating whether connectivity with the remote machine was successful.
        """
        vok = False

        hello_cmd = "echo Hello"
        status, stdout, _ = self.run_cmd(hello_cmd)
        if status == 0 and stdout.strip() == "Hello":
            vok = True

        return vok

    def _create_client(self, session_user: Optional[str] = None) -> paramiko.SSHClient:
        """
            Create an SSHClient to use for running commands and performing FTP operations.

            :param session_user: The user role and associated credentials to use when creating the SSHClient.

            :returns: An SSHClient object connected to the remote machine under the default or specified user credential.
        """
        cl_username = self._username
        cl_password = self._password
        cl_keyfile = self._keyfile
        cl_keyraw = self._keyraw
        cl_keypasswd = self._keypasswd
        cl_allow_agent = self._allow_agent

        now_time = datetime.now()
        begin_time = now_time
        end_time = begin_time + timedelta(seconds=self._aspects.connection_timeout)

        connection_interval = self._aspects.connection_interval
        allowed_connection_exceptions = self._aspects.allowed_connection_exceptions

        while now_time < end_time:

            try:

                if session_user is not None:
                    if session_user not in self._users:
                        errmsg_list = [
                            "No credentials found for the specified user '%s'." % session_user
                        ]
                        errmsg = os.linesep.join(errmsg_list)
                        raise ConfigurationError(errmsg) from None

                    user_creds = self._users[session_user]

                    cl_username = user_creds["username"]
                    cl_password = user_creds["password"]
                    cl_keyfile = user_creds["keyfile"]
                    cl_keypasswd = user_creds["keypasswd"]
                    cl_allow_agent = user_creds["allow_agent"]

                pkey = None
                if cl_keyfile is not None:
                    pkey = self._load_key_file(cl_keyfile, cl_keypasswd)
                elif cl_keyraw is not None:
                    pkey = self._load_key(cl_keyraw, cl_keypasswd)

                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                if self._jump is not None:
                    proxy = paramiko.ProxyCommand(self._jump)
                    ssh_client.connect(self._ipaddr, port=self._port, username=cl_username, password=cl_password,
                                    pkey=pkey, allow_agent=cl_allow_agent, sock = proxy, look_for_keys=self._look_for_keys)
                else:
                    ssh_client.connect(self._ipaddr, port=self._port, username=cl_username, password=cl_password,
                                    pkey=pkey, allow_agent=cl_allow_agent, look_for_keys=self._look_for_keys)
                
                break

            except BaseException as cerr:
                extype = type(cerr)

                if len(allowed_connection_exceptions) > 0 and extype in allowed_connection_exceptions:
                    errmsg = f"SSH connection attempt failed for host={self._ipaddr} begin={begin_time} end={now_time} now={now_time}."
                    logger.error(errmsg)

                    now_time = datetime.now()
                    if now_time > end_time:
                        raise ConnectionError(errmsg) from cerr
                    else:
                        time.sleep(connection_interval)
                else:
                    raise # If the exception we got is not an allowed type, re-raise it


        return ssh_client

    def _directory(self, ssh_client: paramiko.SSHClient, root_dir: str) -> dict:
        """
            Private method that creates a directory listing for the folder.

            :param ssh_client: The SSHClient to use to for geting a list tree.
            :param root_dir: The directory to scan when creating the tree.

            :returns: A dictionary that contains information about the items in the target directory.
        """
        dir_info = {}

        if not self._primitive:
            transport = ssh_client.get_transport()
    
            sftp = paramiko.SFTPClient.from_transport(transport)
            try:
                dir_info = sftp_list_directory(sftp, root_dir, self.lookup_user_by_uid, self.lookup_group_by_uid)
            finally:
                sftp.close()
            
        else:
            dir_info = primitive_list_directory(ssh_client, root_dir)

        return dir_info

    def _directory_exists(self, ssh_client: paramiko.SSHClient, remotedir: str) -> bool:
        """
            Private helper method used to check if the remote directory exists.
        """
        exists = False

        if not self._primitive:

            transport = ssh_client.get_transport()
        
            sftp = paramiko.SFTPClient.from_transport(transport)
            try:
                fsresult = sftp.stat(remotedir)
                if fsresult.st_mode | stat.S_IFDIR:
                    exists = True
            except IOError:
                exists = False
            finally:
                sftp.close()

        else:
            primitive_directory_exists(ssh_client, remotedir)

        return exists

    def _directory_tree(self, ssh_client: paramiko.SSHClient, root_dir: str, depth: int = 1) -> dict:
        """
            Private method that creates a directory tree for the folder.

            :param ssh_client: The SSHClient to use to for geting a list tree.
            :param root_dir: The root directory to scan when creating the tree.
            :param depth: The dept to scan to

            :returns: A dictionary with a tree of information about the directory tree found on the remote system.
        """
        dir_info = {}

        if not self._primitive:
            transport = ssh_client.get_transport()

            sftp = paramiko.SFTPClient.from_transport(transport)
            try:
                dir_info = sftp_list_tree(sftp, root_dir, self.lookup_user_by_uid, self.lookup_group_by_uid, max_depth=depth)
            finally:
                sftp.close()

        else:
            dir_info = primitive_list_tree(ssh_client, root_dir, max_depth=depth)

        return dir_info

    def _get_home_directory(self, aspects: Optional[AspectsCmd] = None) -> str:
        """
            Private method that handles the getting of the home directory for the credential account from a remote machine.

            :param aspects: The run aspects to use when running the command.

            :returns: The remote home directory
        """
        home_dir = None

        home_cmd = 'echo "$HOME"'
        status, stdout, stderr = self.run_cmd(home_cmd, aspects=aspects)
        if status == 0:
            home_dir = stdout.strip()
        
        return home_dir

    def _log_command_result(self, command: str, status: int, stdout: str, stderr: str, exp_status: Union[int, Sequence[int]], logging_pattern: LoggingPattern):
        """
            Private method that handles the logging of command results based on the expected status and logging pattern
            specified.

            :param command: The command that was run.
            :param status: The status code returned from running the command.
            :param stdout: The contents of the standard output from running the command.
            :param stderr: The contents of the error output from running the command.
            :param exp_status: The status code or possible status codes that was expected to be returned from running the command.
            :param logging_pattern: The result logging pattern (LoggingPattern) to use when logging.
        """
        # pylint: disable=no-self-use

        tgt_tag = ""
        if self._target_tag is not None:
            tgt_tag = self._target_tag

        if isinstance(exp_status, int):
            if status == exp_status:
                if logging_pattern == LoggingPattern.ALL_RESULTS or logging_pattern == LoggingPattern.SUCCESS_ONLY:
                    logger.info(TEMPLATE_COMMAND_SUCCESS % (tgt_tag, command, stdout, stderr) )
        else:
            if status in exp_status:
                if logging_pattern == LoggingPattern.ALL_RESULTS or logging_pattern == LoggingPattern.SUCCESS_ONLY:
                    logger.info(TEMPLATE_COMMAND_SUCCESS % (tgt_tag, command, stdout, stderr))
            else:
                if logging_pattern == LoggingPattern.ALL_RESULTS or logging_pattern == LoggingPattern.FAILURE_ONLY:
                    logger.error(TEMPLATE_COMMAND_FAILURE % (tgt_tag, command, stdout, stderr))

        return

    def _run_cmd(self, ssh_runner: Union[paramiko.SSHClient, paramiko.Channel], command: str, exp_status: Union[int, Sequence]=0, user: str = None, pty_params: dict = None, aspects: Optional[AspectsCmd] = None) -> Tuple[int, str, str]:
        """
            Private method that handles the running commands in a generic way so the logic and run pattern code can be shared between agent and session objects.

            :param ssh_runner: A :class:`paramiko.SSHClient` or :class:`paramiko.Channel` object that can be used to run a command on a remote machine.
            :param command: The command that is to be run.
            :param exp_status: The status code or a sequence of possible status codes that are expected to be returned from running the command.
            :param user: The role name of the user account to utilize when looking up the credentials used to connect to the remote host.
            :param pty_params: A dictionary of parameters that are passed to paramiko to get a pty when running commands.
            :param aspects: The run aspects to use when running the command.

            :returns: The status, stderr and stdout from the command that was run.
        """
        # Go through the overrides and if they are not passed use the agent defaults.
        if pty_params is None:
            pty_params = self._pty_params

        if aspects is None:
            aspects = self._aspects

        if user is not None:
            if self._users is None:
                errmsg = "In order to pass a 'user' parameter, you must create the SSHAgent with a 'users' parameter with a dictionary of user credentials."
                raise ConfigurationError(errmsg) from None
            if user not in self._users:
                errmsg = "The specified 'user=%s' was not found in the users credentials provided to SSHAgent."

        completion_toctx = TimeoutContext(aspects.completion_timeout, aspects.completion_interval)
        
        inactivity_timeout = aspects.inactivity_timeout
        inactivity_interval = aspects.inactivity_interval
        monitor_delay = aspects.monitor_delay
        logging_pattern = aspects.logging_pattern

        status, stdout, stderr = None, None, None

        this_thr = threading.current_thread()
        monmsg= "Thread failed to exit monitored scope. thid=%s thname=%s cmd=%s" % (this_thr.ident, this_thr.name, command)

        # Run the command using the SINGULAR pattern, we run it once and then return the result
        if aspects.action_pattern == ActionPattern.SINGLE_CALL:

            # Setup a monitored scope for the call to the remote device in case of timeout failure
            with MonitoredScope("RUNCMD-SINGULAR", monmsg, completion_toctx, notify_delay=monitor_delay) as _:

                status, stdout, stderr = self._ssh_execute_command(ssh_runner, command, pty_params=pty_params,
                    inactivity_timeout=inactivity_timeout, inactivity_interval=inactivity_interval)

            self._log_command_result(command, status, stdout, stderr, exp_status, logging_pattern)

        # DO_UNTIL_SUCCESS, run the command until we get a successful expected result or a completion timeout has occured
        elif aspects.action_pattern == ActionPattern.DO_UNTIL_SUCCESS:

            completion_toctx.mark_begin()

            while True:

                # Setup a monitored scope for the call to the remote device in case of timeout failure
                with MonitoredScope("RUNCMD-DO_UNTIL_SUCCESS", monmsg, completion_toctx, notify_delay=monitor_delay) as _:
                    status, stdout, stderr = self._ssh_execute_command(ssh_runner, command, pty_params=pty_params,
                        inactivity_timeout=inactivity_timeout, inactivity_interval=inactivity_interval)

                self._log_command_result(command, status, stdout, stderr, exp_status, logging_pattern)

                if isinstance(exp_status, int):
                    if status == exp_status:
                        break
                elif status in exp_status:
                    break

                if completion_toctx.final_attempt:
                    what_for="command success"
                    details = [
                        "CMD: %s" % command,
                        "STDOUT:",
                        indent_lines(stdout, 1),
                        "STDERR:",
                        indent_lines(stderr, 1),
                    ]
                    toerr = completion_toctx.create_timeout(what_for=what_for, detail=details)
                    raise toerr

                elif not completion_toctx.should_continue():
                    completion_toctx.mark_final_attempt()

                time.sleep(completion_toctx.interval)

        # DO_WHILE_SUCCESS, run the command while it is succeeds or a completion timeout has occured
        elif aspects.action_pattern == ActionPattern.DO_WHILE_SUCCESS:

            completion_toctx.mark_begin()

            while True:

                with MonitoredScope("RUNCMD-DO_WHILE_SUCCESS", monmsg, completion_toctx, notify_delay=monitor_delay) as _:
                    status, stdout, stderr = self._ssh_execute_command(ssh_runner, command, pty_params=pty_params,
                        inactivity_timeout=inactivity_timeout, inactivity_interval=inactivity_interval)

                self._log_command_result(command, status, stdout, stderr, exp_status, logging_pattern)

                if isinstance(exp_status, int):
                    if status != exp_status:
                        break
                elif status not in exp_status:
                    break

                if completion_toctx.final_attempt:
                    what_for="command failure"
                    details = [
                        "CMD: %s" % command,
                        "STDOUT:",
                        indent_lines(stdout, 1),
                        "STDERR:",
                        indent_lines(stderr, 1),
                    ]
                    toerr = completion_toctx.create_timeout(what_for=what_for, detail=details)
                    raise toerr

                elif not completion_toctx.should_continue():
                    completion_toctx.mark_final_attempt()

                time.sleep(completion_toctx.interval)

        elif aspects.action_pattern == ActionPattern.SINGLE_CONNECTED_CALL or aspects.action_pattern == ActionPattern.DO_UNTIL_CONNECTION_FAILURE:
            errmsg = "SshAgent and SshSession currently do not support the SINGLE_CONNECTED_CALL or DO_UNTIL_CONNECTION_FAILURE action patterns."
            raise SemanticError(errmsg) from None
        else:
            errmsg = "SshBase: Unknown ActionPattern encountered. action_pattern={}".format(aspects.action_pattern)
            raise SemanticError(errmsg) from None

        return status, stdout, stderr

    def _file_exists(self, ssh_client: paramiko.SSHClient, remotepath: str) -> bool:
        """
            Private helper method used to check if the remote file exists.
        """
        exists = False

        if not self._primitive:
            transport = ssh_client.get_transport()

            sftp = paramiko.SFTPClient.from_transport(transport)
            try:
                fsresult = sftp.stat(remotepath)
                if not (fsresult.st_mode | stat.S_IFDIR):
                    exists = True
            except FileNotFoundError as ferr:
                exists = False
            finally:
                sftp.close()
        else:
            exists = primitive_file_exists(ssh_client, remotepath)

        return exists

    def _file_pull(self, ssh_client: paramiko.SSHClient, remotepath: str, localpath: str):
        """
            Private helper method used to pull a remote file to a local file path.
        """
        if not self._primitive:
            transport = ssh_client.get_transport()
            
            sftp = paramiko.SFTPClient.from_transport(transport)
            try:
                sftp.get(remotepath, localpath)
            finally:
                sftp.close()

        else:
            primitive_file_pull(ssh_client, remotepath, localpath)

        return

    def _file_push(self, ssh_client: paramiko.SSHClient, localpath: str, remotepath: str):
        """
            Private helper method used to push a local file to a remote file path.
        """
        if not self._primitive:
            transport = ssh_client.get_transport()
            
            sftp = paramiko.SFTPClient.from_transport(transport)
            try:
                sftp.put(localpath, remotepath)
            finally:
                sftp.close()
            
        else:
            primitive_file_push(ssh_client, localpath, remotepath)

        return

    def _load_key(self, keyraw: str, keypasswd: str):

        keybuffer = StringIO(keyraw)

        pkey = None
        try:
            pkey = paramiko.RSAKey.from_private_key(keybuffer, password=keypasswd)
        except Exception as klerr:
            pass
        
        if pkey is None:
            try:
                pkey = paramiko.ECDSAKey.from_private_key(keybuffer, password=keypasswd)
            except:
                pass

        if pkey is None:
            try:
                pkey = paramiko.Ed25519Key.from_private_key(keybuffer, password=keypasswd)
            except:
                pass

        if pkey is None:
            errmsg = f"ERROR: Unable to load private from raw content."
            raise ConfigurationError(errmsg)

        return

    def _load_key_file(self, keyfile: str, keypasswd: str):

        keyfile = os.path.expanduser(os.path.expandvars(keyfile))

        pkey = None
        try:
            pkey = paramiko.RSAKey.from_private_key_file(keyfile, password=keypasswd)
        except Exception as klerr:
            pass
        
        if pkey is None:
            try:
                pkey = paramiko.ECDSAKey.from_private_key_file(keyfile)
            except:
                pass

        if pkey is None:
            try:
                pkey = paramiko.Ed25519Key.from_private_key_file(keyfile)
            except:
                pass

        if pkey is None:
            errmsg = f"ERROR: Unable to load private keyfile={keyfile}"
            raise ConfigurationError(errmsg)

        return pkey

    def _ssh_execute_command(self, ssh_runner, command: str, pty_params=None, inactivity_timeout: float=DEFAULT_SSH_TIMEOUT, inactivity_interval: float=DEFAULT_SSH_RETRY_INTERVAL, chunk_size: int=1024) -> Tuple[int, str, str]: # pylint: disable=no-self-use
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
        status, stdout, stderr = ssh_execute_command(ssh_runner, command, pty_params=pty_params, inactivity_timeout=inactivity_timeout, inactivity_interval=inactivity_interval, chunk_size=chunk_size)
        return status, stdout, stderr
