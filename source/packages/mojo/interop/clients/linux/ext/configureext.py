
from typing import TYPE_CHECKING, Optional

import os
import tempfile
import weakref

from mojo.errors.exceptions import CommandError

from mojo.xmods.credentials.sshcredential import SshCredential
from mojo.xmods.interfaces.isystemcontext import ISystemContext
from mojo.xmods.xformatting import format_command_result

from mojo.interop.clients.clientsourcepackager import ClientSourcePackager
import mojo.interop.protocols.tasker.taskerservice as tasker_service

if TYPE_CHECKING:
    from mojo.interop.clients.linux.linuxclient import LinuxClient


TEMPLATE_FILE_SUDO_CONFIG = "/etc/sudoers.d/77-automation-{username}"

DIR_TASKER_SERVICE = os.path.dirname(tasker_service.__file__)

FILE_TASKER_SERVICE_BIN = os.path.join(DIR_TASKER_SERVICE, "linux", "taskerservice")

FILE_TASKER_SERVICE_SVC_TEMPLATE = os.path.join(DIR_TASKER_SERVICE, "linux", "tasker-service.template")


class ConfigureExt:

    def __init__(self, client: "LinuxClient"):
        self._client_ref = weakref.ref(client)
        return

    @property
    def client(self) -> "LinuxClient":
        return self._client_ref()

    def configure_tasker_service(self, remote_source_root: str, sudo_username: Optional[str] = None, sudo_password: Optional[str] = None,
                                 sys_context: Optional[ISystemContext] = None):

        client = self.client

        if sudo_username is None:
            sshcred: SshCredential = client.get_credentials_by_category("ssh")[0]

            sudo_username = sshcred.username
        
        with client.ssh.open_session(sys_context=sys_context) as session:

            status, stdout, stderr = session.run_cmd('echo "$HOME"')
            if status != 0:
                errmsg = "Unable to obtain remote home directory for client."
                raise Exception(errmsg)

            remote_home = stdout.strip().rstrip(os.sep)

            remote_source_root = remote_source_root.strip()
            if remote_source_root.startswith("~"):
                remote_source_root = remote_source_root.replace("~", remote_home)

            tasker_server_bin_rmt = os.path.join(remote_source_root, ".venv/bin/taskerservice")
            tasker_server_packages_rmt = os.path.join(remote_source_root, "source", "packages")

            session.file_push(FILE_TASKER_SERVICE_BIN, tasker_server_bin_rmt)

            chmod_cmd = f"chmod +x {tasker_server_bin_rmt}"
            status, stdout, stderr = session.run_cmd(chmod_cmd)
            if status != 0:
                errmsg = format_command_result(f"Unable to make file='{tasker_server_bin_rmt}' executable",
                                            status, stdout, stderr, target=client.ipaddr)
                raise CommandError(errmsg, status, stdout, stderr)

            # If we were able to install the `taserserver` binary, then setup the service to automatically
            # run via systemd

            tasker_server_cfg_fill_dict = {
                "username": sudo_username,
                "group": sudo_username,
                "tasker-binary": tasker_server_bin_rmt,
                "tasker-packages": tasker_server_packages_rmt
            }

            ts_cfg_template_content = None
            with open(FILE_TASKER_SERVICE_SVC_TEMPLATE, 'r') as tscfg:
                ts_cfg_template_content = tscfg.read()

            tasker_server_cfg_content = ts_cfg_template_content.format(**tasker_server_cfg_fill_dict)

            tasker_server_cfg_local = tempfile.mktemp()
            try:
                with open(tasker_server_cfg_local, 'w+') as tscf:
                    tscf.write(tasker_server_cfg_content)
                
                self.install_systemd_service("tasker", sudo_username, tasker_server_cfg_local, pidfolder=f"/var/run/tasker",
                                             optfolder="/opt/tasker", sys_context=session)
            finally:
                os.remove(tasker_server_cfg_local)

        return

    def deploy_source_package(self, source_root: str, package_name: str, remote_source_root: str, cache_dir: Optional[str] = None,
                              force_update: Optional[bool]=False, sys_context: Optional[ISystemContext] = None):

        client = self.client

        if cache_dir is None:
            cache_dir = os.path.join(source_root, ".cache")
        
        packager = ClientSourcePackager(source_root, cache_dir)

        skip_if_exists = not force_update

        packager.create_zip_package(package_name, skip_if_exists=skip_if_exists)

        source_env = packager.get_environment()

        with client.ssh.open_session(sys_context=sys_context) as session:

            python_version = self.get_python_version(sys_context=session)
            python_path_list = [
                f"{remote_source_root}/source/packages",
                f"{remote_source_root}/source/testroots/testplus",
                f"{remote_source_root}/.venv/lib/{python_version}/site-packages"
            ]
            python_path = ":".join(python_path_list)
        
            install_env = source_env.copy()
            install_env["PYTHON_VERSION"] = python_version
            install_env["PYTHONPATH"] = python_path

            packager.deploy_zip_package_via_ssh(session, package_name, install_env, remote_source_root)

        return

    def enabled_no_password_sudo(self, sudo_username: Optional[str] = None, sudo_password: Optional[str] = None,
                                 sys_context: Optional[ISystemContext] = None):
        
        client = self.client

        if sudo_username is None:
            sshcred: SshCredential = client.get_credentials_by_category("ssh")[0]

            sudo_username = sshcred.username
            sudo_password = sshcred.password

        fill_dict = {"username": sudo_username}
        user_cfg_file = TEMPLATE_FILE_SUDO_CONFIG.format(**fill_dict)

        with client.ssh.open_session(sys_context=sys_context) as session:

            sudo_file_exists_cmd = f"sudo bash -c \"[[ -f {user_cfg_file} ]] && echo 0 || echo 1\""
            status, stdout, stderr = session.run_cmd(sudo_file_exists_cmd)
            if int(stdout.strip()) == 1:

                sudo_grp_cmd = f"echo '{sudo_password}' | sudo -S usermod -aG sudo {sudo_username}"
                status, stdout, stderr = session.run_cmd(sudo_grp_cmd)
                if status != 0:
                    errmsg = format_command_result(f"Error while attempting to add `{sudo_username}` to the 'sudo' user group.",
                                                status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                    raise CommandError(errmsg, status, stdout, stderr)

                sudo_user_cfg_cmd =  f"echo '{sudo_password}' | sudo -S bash -c \"echo '{sudo_username} ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo -f {user_cfg_file}\""
                status, stdout, stderr = session.run_cmd(sudo_user_cfg_cmd)
                if status != 0:
                    errmsg = format_command_result(f"Error while installing sudo config for user `{sudo_username}`.",
                                                status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                    raise CommandError(errmsg, status, stdout, stderr)
        
        return
    
    def get_python_version(self, sys_context: Optional[ISystemContext] = None):

        client = self.client

        python_version = None

        with client.ssh.open_session(sys_context=sys_context) as session:

            getpyver_cmd = "python3 -c \"import platform; print('python{}.{}'.format(*platform.python_version_tuple()[:2]))\""
            status, stdout, stderr = session.run_cmd(getpyver_cmd)
            if status != 0:
                errmsg = format_command_result(f"Error while attempting to get the python version from the remote machine.",
                                            status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                raise CommandError(errmsg, status, stdout, stderr)

            python_version = stdout.strip()

        return python_version

    def install_systemd_service(self, svcname: str, svcuser: str, source_svc_config_file: str, pidfolder: Optional[str] =  None,
                                optfolder: Optional[str] =  None, sys_context: Optional[ISystemContext] = None):

        client = self.client

        final_dest_svc_config_file = f"/etc/systemd/system/{svcname}.service"
        tmp_dest_svc_config_file = f"/tmp/{svcname}.service"

        with client.ssh.open_session(sys_context=sys_context) as session:

            if optfolder is not None:
                mkdir_cmd = f"sudo mkdir -p {optfolder}"
                status, stdout, stderr = session.run_cmd(mkdir_cmd)
                if status != 0:
                    errmsg = format_command_result(f"Error while attempting to create the opt folder for `{svcname}`.",
                                                status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                    raise CommandError(errmsg, status, stdout, stderr)

                chown_cmd = f"sudo chown {svcuser}:{svcuser} {optfolder}"
                status, stdout, stderr = session.run_cmd(chown_cmd)
                if status != 0:
                    errmsg = format_command_result(f"Error while attempting to change the ownership of the opt folder for `{svcname}`.",
                                                status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                    raise CommandError(errmsg, status, stdout, stderr)

            if pidfolder is not None:
                mkdir_cmd = f"sudo mkdir -p {pidfolder}"
                status, stdout, stderr = session.run_cmd(mkdir_cmd)
                if status != 0:
                    errmsg = format_command_result(f"Error while attempting to create the pid folder for `{svcname}`.",
                                                status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                    raise CommandError(errmsg, status, stdout, stderr)

                chown_cmd = f"sudo chown {svcuser}:{svcuser} {pidfolder}"
                status, stdout, stderr = session.run_cmd(chown_cmd)
                if status != 0:
                    errmsg = format_command_result(f"Error while attempting to change the ownership of pid folder for `{svcname}`.",
                                                status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                    raise CommandError(errmsg, status, stdout, stderr)

            stop_svc_cmd = f"sudo systemctl stop {svcname}"
            session.run_cmd(stop_svc_cmd)

            rm_svc_cfg_cmd = f"sudo rm -f {final_dest_svc_config_file}"
            status, stdout, stderr = session.run_cmd(rm_svc_cfg_cmd)
            if status != 0:
                errmsg = format_command_result(f"Error while attempting to remove the config file for `{svcname}` service.",
                                            status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                raise CommandError(errmsg, status, stdout, stderr)

            session.file_push(source_svc_config_file, tmp_dest_svc_config_file)

            enable_svc_cmd = f"sudo cp -f {tmp_dest_svc_config_file} {final_dest_svc_config_file}"
            status, stdout, stderr = session.run_cmd(enable_svc_cmd)
            if status != 0:
                errmsg = format_command_result(f"Error while attempting to install `{svcname}` service config file.",
                                            status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                raise CommandError(errmsg, status, stdout, stderr)

            chown_cmd = f"sudo chown root {final_dest_svc_config_file}"
            status, stdout, stderr = session.run_cmd(chown_cmd)
            if status != 0:
                errmsg = format_command_result(f"Error while attempting to change `{svcname}` service config file owner.",
                                            status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                raise CommandError(errmsg, status, stdout, stderr)

            chmod_cmd = f"sudo chmod 644 {final_dest_svc_config_file}"
            status, stdout, stderr = session.run_cmd(chmod_cmd)
            if status != 0:
                errmsg = format_command_result(f"Error while attempting to change `{svcname}` service config permissions.",
                                            status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                raise CommandError(errmsg, status, stdout, stderr)

            daemon_reload_cmd = f"sudo systemctl daemon-reload"
            status, stdout, stderr = session.run_cmd(daemon_reload_cmd)
            if status != 0:
                errmsg = format_command_result(f"Error while attempting to reload systemclt daemon.",
                                            status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                raise CommandError(errmsg, status, stdout, stderr)

            start_svc_cmd = f"sudo systemctl enable {svcname}"
            status, stdout, stderr = session.run_cmd(start_svc_cmd)
            if status != 0:
                errmsg = format_command_result(f"Error while attempting to start `{svcname}` service.",
                                            status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                raise CommandError(errmsg, status, stdout, stderr)

            if not self.is_service_running(svcname, sys_context=session):

                start_svc_cmd = f"sudo systemctl start {svcname}"
                status, stdout, stderr = session.run_cmd(start_svc_cmd)
                if status != 0:
                    errmsg = format_command_result(f"Error while attempting to start `{svcname}` service.",
                                                status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                    raise CommandError(errmsg, status, stdout, stderr)

        return
    
    def is_service_running(self, svcname: str, sys_context: Optional[ISystemContext] = None):

        client = self.client

        svc_running = False

        with client.ssh.open_session(sys_context=sys_context) as session:
            chk_svc_running_cmd = "systemctl is-active --quiet tasker && echo $?"
            status, stdout, stderr = session.run_cmd(chk_svc_running_cmd)
            if status != 0:
                if stderr != "":
                    errmsg = format_command_result(f"Error while attempting to start `{svcname}` service.",
                                                status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                    raise CommandError(errmsg, status, stdout, stderr)
                else:
                    svc_running = False
            else:
                svc_running = True

        return svc_running