
__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []


from typing import Optional, Type, TYPE_CHECKING

import os
import weakref

from mojo.errors.exceptions import CommandError, SemanticError

from mojo.interfaces.isystemcontext import ISystemContext
from mojo.xmods.xformatting import format_command_result

from mojo.interop.protocols.ssh.sshagent import SshSession

if TYPE_CHECKING:
    from mojo.interop.clients.linux.linuxclient import LinuxClient

class CommandsExt:

    def __init__(self, client: "LinuxClient"):
        self._client_ref = weakref.ref(client)
        return

    @property
    def client(self) -> "LinuxClient":
        return self._client_ref()

    def cifs_mount(self, share: str, mpoint: str, username: Optional[str]=None,
                   password: Optional[str]=None, domain: Optional[str]=None,
                   basis_session: Optional[ISystemContext]=None):

        status, stdout, stderr = None, None, None

        sysctx = self.client.get_default_system_context()

        session: ISystemContext
        with sysctx.open_session(basis_session=basis_session) as session:
            mparent = os.path.dirname(mpoint)
            if not session.directory_exists(mparent):
                errmsg = f"The parent directory '{mparent}' of the specified mount point must exist. mpoint={mpoint}"
                raise SemanticError(errmsg)

            mount_cmd = f"mkdir -p {mpoint}"
            status, stderr, stdout = session.run_cmd()
            if status != 0:
                errmsg = f"Error attempting to create mount point mpoint={mpoint}."
                errmsg = format_command_result(errmsg, mount_cmd, status, stdout, stderr, exp_status=0)
                raise CommandError(errmsg, status, stdout, stderr)

            if username is not None and password is None:
                errmsg = "If you provide a username then you must provide a password."
                raise SemanticError(errmsg)
            
            if domain is not None and username is None:
                errmsg = "If you provide a domain you must provide a username and password."
                raise SemanticError(errmsg)
    
            options = ""
            if username is not None:
                options += f"-o username=\"{username}\" "

            if password is not None:
                options += f"password=\"{password}\" "

            if domain is not None:
                options += f"domain={domain}"

            mnt_cmd = f"mount -t cifs \"{share}\" \"{mpoint}\""
            status, stderr, stdout = session.run_cmd(mnt_cmd)
            if status != 0:
                ipaddr = self.client.ipaddr
                errmsg = f"Error attempting to mount cifs share={share} on mpoint={mpoint}."
                errmsg = format_command_result(errmsg, mnt_cmd, status, stdout, stderr, exp_status=0, target=ipaddr)
                raise CommandError(errmsg, status, stdout, stderr)

        return
    
    def nfs_mount(self, host:str, export: str, mpoint: str, basis_session: Optional[ISystemContext]=None):
        status, stdout, stderr = None, None, None

        sysctx = self.client.get_default_system_context()

        session: ISystemContext
        with sysctx.open_session(basis_session=basis_session) as session:

            mparent = os.path.dirname(mpoint)
            if not session.directory_exists(mparent):
                errmsg = f"The parent directory '{mparent}' of the specified mount point must exist. mpoint={mpoint}"
                raise SemanticError(errmsg)

            mkdir_cmd = f"mkdir -p {mpoint}"
            status, stderr, stdout = session.run_cmd(mkdir_cmd)
            if status != 0:
                errmsg = f"Error attempting to create mount point mpoint={mpoint}."
                errmsg = format_command_result(errmsg, mkdir_cmd, status, stdout, stderr, exp_status=0)
                raise CommandError(errmsg, status, stdout, stderr)

            mnt_cmd = f"mount -t nfs {host}:\"{export}\" \"{mpoint}\""
            status, stderr, stdout = session.run_cmd(mnt_cmd)
            if status != 0:
                ipaddr = self.client.ipaddr
                errmsg = f"Error attempting to mount nfsmoun export={export} on mpoint={mpoint}."
                errmsg = format_command_result(errmsg, mnt_cmd, status, stdout, stderr, exp_status=0, target=ipaddr)
                raise CommandError(errmsg, status, stdout, stderr)

        return

    def system_logger(self, msg: str, basis_session: Optional[ISystemContext]=None):
        
        status, stdout, stderr = None, None, None

        sysctx = self.client.get_default_system_context()

        session: ISystemContext
        with sysctx.open_session(basis_session=basis_session) as session:
            command = f'sudo logger "{msg}"'
            status, stderr, stdout = session.run_cmd(command)
            if status != 0:
                ipaddr = self.client.ipaddr
                errmsg = f"Error attempting to log a message."
                errmsg = format_command_result(errmsg, command, status, stdout, stderr, exp_status=0, target=ipaddr)
                raise CommandError(errmsg, status, stdout, stderr)

        return

    def umount(self, mpoint: str, flags:str="", basis_session: Optional[ISystemContext]=None):
        status, stdout, stderr = None, None, None

        sysctx = self.client.get_default_system_context()

        session: ISystemContext
        with sysctx.open_session(basis_session=basis_session) as session:

            mnt_cmd = f"umount {flags} \"{mpoint}\""
            status, stderr, stdout = session.run_cmd(mnt_cmd)
            if status != 0:
                errmsg = f"Error attempting to unmount mpoint={mpoint}."
                errmsg = format_command_result(errmsg, mnt_cmd, status, stdout, stderr, exp_status=0)
                raise CommandError(errmsg, status, stdout, stderr)

        return