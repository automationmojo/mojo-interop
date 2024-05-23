
__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []

from typing import Dict, Optional

import fnmatch
import hashlib
import logging
import os
import tempfile
import zipfile

logger = logging.getLogger()

from mojo.interfaces.isystemcontext import ISystemContext

from mojo.interop.protocols.ssh.sshagent import SshAgent

class ClientSourcePackager:

    EXCLUDE_DIRECTORY_LEAFS = [
        ".cache",
        ".git",
        ".venv",
        ".vscode",
        "docs",
        "userguide",
        "workspaces"
    ]

    EXCLUDE_FILE_LEAFS = [
        ".gitattributes",
        ".gitignore",
        ".env"
    ]

    EXCLUDE_FILENAME_MATCHES = [
        "*.pyc"
    ]

    def __init__(self, source_root: str, cache_dir: str):
        self._source_root = os.path.abspath(os.path.expandvars(os.path.expanduser(source_root)))
        self._cache_dir = os.path.abspath(os.path.expandvars(os.path.expanduser(cache_dir)))
        return
    
    def create_zip_package(self, package_name: str, compresslevel: int=7, skip_if_exists=True):

        package_name = package_name.strip()
        if not package_name.endswith(".zip"):
            package_name = f"{package_name}.zip"

        package_base, _ = os.path.splitext(package_name)
        package_digest_name = f"{package_base}.sha256"

        if not os.path.exists(self._cache_dir):
            os.makedirs(self._cache_dir)

        zipfilename = os.path.join(self._cache_dir, package_name)
        digestfilename = os.path.join(self._cache_dir, package_digest_name)

        if os.path.exists(zipfilename) and os.path.exists(digestfilename):

            if skip_if_exists:
                print(f"Using pre-existing cached package {zipfilename}.")
                return
            
        if os.path.exists(zipfilename):

            print(f"Removing pre-existing cached package {zipfilename}.")
            os.remove(zipfilename)

        if os.path.exists(digestfilename):
            os.remove(digestfilename)

        with zipfile.ZipFile(zipfilename, mode='w', compression=zipfile.ZIP_DEFLATED, compresslevel=compresslevel) as zf:

            sroot_path_len = len(self._source_root)

            for dirpath, _, filenames in os.walk(self._source_root, topdown=True):

                dirleaf = dirpath[sroot_path_len:].lstrip(os.sep)

                if any(dirleaf.startswith(expfx) for expfx in self.EXCLUDE_DIRECTORY_LEAFS):
                    logger.info(f"Skipping excluded leaf directory {dirleaf}.")
                    continue

                for fname in filenames:

                    filefull = os.path.join(dirpath, fname)
                    
                    afile = fname
                    if dirleaf != "":
                        afile = os.path.join(dirleaf, fname)

                    if afile in self.EXCLUDE_FILE_LEAFS:
                        logger.info(f"Skipping excluded file leaf {afile}.")

                    if any(fnmatch.fnmatch(fname, expat) for expat in self.EXCLUDE_FILENAME_MATCHES):
                        logger.info(f"Skipping file with excluded match pattern {afile}.")
                    
                    zf.write(filefull, afile)

        sha256_digest = hashlib.sha256(open(zipfilename,'rb').read()).hexdigest()
        with open(digestfilename, mode='w+') as df:
            df.write(sha256_digest)

        return
    
    def deploy_zip_package_via_ssh(self, session: ISystemContext, package_name: str, package_env: Dict[str, str], destination: str,
                                   force_update: bool = False):

        package_name = package_name.strip()
        if not package_name.endswith(".zip"):
            package_name = f"{package_name}.zip"

        destination = destination.strip()

        status, stdout, stderr = session.run_cmd('echo "$HOME"')
        if status != 0:
            errmsg = "Unable to obtain remote home directory for client."
            raise Exception(errmsg)
        
        rmt_home = stdout.strip()
        if destination.startswith("~"):
            destination = destination.replace("~", rmt_home)

        lcl_filename = os.path.join(self._cache_dir, package_name)
        rmt_filename = os.path.join(rmt_home, package_name)

        if force_update:
            rm_pkg_cmd = f"sudo rm -f {rmt_filename}"
            status, stdout, stderr = session.run_cmd(rm_pkg_cmd)
            if status != 0:
                errmsg = "Unable to remove remote package. file={rmt_filename}."
                raise RuntimeError(errmsg)
            
            rm_source_cmd = f"sudo rm -fr {destination}"
            status, stdout, stderr = session.run_cmd(rm_source_cmd)
            if status != 0:
                errmsg = "Unable to remove remote source directory. file={destination}."
                raise RuntimeError(errmsg)

        session.file_push(lcl_filename, rmt_filename)

        ensure_dest = f"mkdir -p {destination}"
        status, stdout, stderr = session.run_cmd(ensure_dest)
        if status != 0:
            errmsg = "Error attempting to create the destination directory."
            raise RuntimeError(errmsg)

        apt_update_cmd = f"sudo apt update"
        status, stdout, stderr = session.run_cmd(apt_update_cmd)
        if status != 0:
            errmsg = "Error attempting to the apt package list."
            raise RuntimeError(errmsg)

        ensure_cmd = f"apt list --installed | grep -E '^[b]uild-essential/[a-z]+'"
        status, stdout, stderr = session.run_cmd(ensure_cmd)
        if status != 0:
            # If the 'zip' package is not found, install it.
            install_cmd = "sudo DEBIAN_FRONTEND=noninteractive apt -yq install build-essential"
            status, stdout, stderr = session.run_cmd(install_cmd)
            if status != 0:
                errmsg = "Unable to install 'build-essential' apt package dependency."
                raise RuntimeError(errmsg)
            
        ensure_cmd = f"apt list --installed | grep -E '^[p]ython3-dev/[a-z]+'"
        status, stdout, stderr = session.run_cmd(ensure_cmd)
        if status != 0:
            # If the 'zip' package is not found, install it.
            install_cmd = "sudo DEBIAN_FRONTEND=noninteractive apt -yq install python3-dev"
            status, stdout, stderr = session.run_cmd(install_cmd)
            if status != 0:
                errmsg = "Unable to install 'python3-dev' apt package dependency."
                raise RuntimeError(errmsg)


        ensure_unzip_cmd = f"which unzip"
        status, stdout, stderr = session.run_cmd(ensure_unzip_cmd)
        if status != 0:
            # If the 'zip' package is not found, install it.
            install_zip_cmd = "sudo DEBIAN_FRONTEND=noninteractive apt -yq install zip"
            status, stdout, stderr = session.run_cmd(install_zip_cmd)
            if status != 0:
                errmsg = "Unable to install 'zip' apt package dependency."
                raise RuntimeError(errmsg)

        unzip_command = f"unzip -od {destination} {rmt_filename}"
        status, stdout, stderr = session.run_cmd(unzip_command)
        if status != 0:
            errmsg_lines = [
                "Unable to unzip the package archive on the remote client.",
                f"STDERR: {stderr}"
            ]
            errmsg = os.linesep.join(errmsg_lines)
            raise RuntimeError(errmsg)

        ensure_poetry_cmd = f"bash -l -c \" which poetry\""
        status, stdout, stderr = session.run_cmd(ensure_poetry_cmd)
        if status != 0:
            # If the 'zip' package is not found, install it.
            install_poetry_cmd = "bash -l -c \"curl -sSL https://install.python-poetry.org | python3 -\""
            status, stdout, stderr = session.run_cmd(install_poetry_cmd)
            if status != 0:
                errmsg = "Unable to install 'poetry' package manager."
                raise RuntimeError(errmsg)

        poetry_clr_cache_cmd = "bash -l -c \" poetry cache clear --no-interaction --all .\""
        status, stdout, stderr = session.run_cmd(poetry_clr_cache_cmd)
        if status != 0:
            errmsg_lines = [
                "Failed to clear the poetry cache.",
                f"STDERR: {stderr}"
            ]
            errmsg = os.linesep.join(errmsg_lines)
            raise RuntimeError(errmsg)
        
        rehome_command = f"bash -l -c \"cd {destination}; {destination}/repository-setup/rehome-repository --skip-workspaces\""
        status, stdout, stderr = session.run_cmd(rehome_command)
        if status != 0:
            errmsg_lines = [
                "Unable to rehome the remote repository.",
                f"STDERR: {stderr}"
            ]
            errmsg = os.linesep.join(errmsg_lines)
            raise RuntimeError(errmsg)

        setup_command = f"bash -l -c \"cd {destination}; EXTRA_POETRY_SETUP_FLAGS='--without dev' {destination}/development/setup-environment reset\""
        status, stdout, stderr = session.run_cmd(setup_command)
        if status != 0:
            errmsg_lines = [
                "Unable to setup the remote automation environment on the remote client.",
                f"STDERR: {stderr}"
            ]
            errmsg = os.linesep.join(errmsg_lines)
            raise RuntimeError(errmsg)
        
        lcl_env_file = tempfile.mktemp()
        with open(lcl_env_file, 'w+') as envf:
            for vname, vval in package_env.items():
                envf.write(f"{vname}={vval}{os.linesep}")

        rmt_env_file = os.path.join(destination, ".env")
        session.file_push(lcl_env_file, rmt_env_file)

        return

    def get_environment(self):
        """
            Gets the information from the .env file of the source package location.
        """
        
        environment = {}
        
        env_file = os.path.join(self._source_root, ".env")
        if os.path.exists(env_file):

            env_lines = None
            with open(env_file, 'r') as envf:
                env_lines = envf.readlines()

                for nxtline in env_lines:
                    nxtline = nxtline.strip()

                    if nxtline == "":
                        continue

                    if nxtline[0] == "#":
                        continue

                    if nxtline.find("=") > -1:
                        vname, vval = nxtline.split("=", maxsplit=1)

                        vname = vname.strip()
                        vval = vval.strip()

                        environment[vname] = vval

        return environment