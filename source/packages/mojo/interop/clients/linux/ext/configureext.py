
from typing import TYPE_CHECKING, Optional

import weakref

TEMPLATE_FILE_SUDO_CONFIG = "/etc/sudoers.d/77-automation-%(username)s"

from mojo.errors.exceptions import CommandError
from mojo.interop.protocols.ssh.sshagent import SshAgent
from mojo.xmods.credentials.sshcredential import SshCredential
from mojo.xmods.xformatting import format_command_result

if TYPE_CHECKING:
    from mojo.interop.clients.linux.linuxclient import LinuxClient

class ConfigureExt:

    def __init__(self, client: "LinuxClient"):
        self._client_ref = weakref.ref(client)
        return

    @property
    def client(self) -> "LinuxClient":
        return self._client_ref()

    def enabled_no_password_sudo(self, sudo_username: Optional[str] = None, sudo_password: Optional[str] = None):
        
        client = self.client

        if sudo_username is None:
            sshcred: SshCredential = self.client.get_credentials_by_category("ssh")

            sudo_username = sshcred.username
            sudo_password = sshcred.password

        fill_dict = {"username": sudo_username}

        sudo_grp_cmd = f"echo '{sudo_password}' | sudo -S usermod -aG sudo username"
        status, stdout, stderr = client.ssh.run_cmd(sudo_grp_cmd)
        if status != 0:
            errmsg = format_command_result(f"Error while attempting to add `{sudo_username}` to the 'sudo' user group.",
                                           status, stdout, stderr, exp_status=[0], target=client.ipaddr)
            raise CommandError(errmsg, status, stdout, stderr)

        user_cfg_file = TEMPLATE_FILE_SUDO_CONFIG.format(fill_dict)

        sudo_user_cfg_cmd =  f"echo '{sudo_password}' | sudo -S echo '{sudo_username} ALL=(ALL) NOPASSWD: ALL' > {user_cfg_file}"
        status, stdout, stderr = client.ssh.run_cmd(sudo_user_cfg_cmd)
        if status != 0:
            errmsg = format_command_result(f"Error while installing sudo config for user `{sudo_username}`.",
                                           status, stdout, stderr, exp_status=[0], target=client.ipaddr)
            raise CommandError(errmsg, status, stdout, stderr)
        
        return