
import fnmatch
import hashlib
import logging
import os
import zipfile

logger = logging.getLogger()

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
        ".gitignore"
    ]

    EXCLUDE_FILENAME_MATCHES = [
        "*.pyc"
    ]

    def __init__(self, source_root: str, cache_dir: str):
        self._source_root = os.path.abspath(os.path.expandvars(os.path.expanduser(source_root)))
        self._cache_dir = cache_dir
        return
    
    def create_zip_package(self, package_name: str, compresslevel: int=7):

        package_name = package_name.strip()
        if not package_name.endswith(".zip"):
            package_name = f"{package_name}.zip"

        package_base, _ = os.path.splitext(package_name)
        package_digest_name = f"{package_base}.sha256"

        if not os.path.exists(self._cache_dir):
            os.makedirs(self._cache_dir)

        zipfilename = os.path.join(self._cache_dir, package_name)
        digestfilename = os.path.join(self._cache_dir, package_digest_name)

        with zipfile.ZipFile(zipfilename, mode='w', compression=zipfile.ZIP_DEFLATED, compresslevel=compresslevel) as zf:

            sroot_path_len = len(self._source_root)

            for dirpath, _, filenames in os.walk(self._source_root, topdown=True):

                dirleaf = dirpath[sroot_path_len:]

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
                    
                    logger.debug(f"Archiving: {filefull}")
                    zf.write(filefull, afile)

        sha256_digest = hashlib.sha256(open(zipfilename,'rb').read()).hexdigest()
        with open(digestfilename, mode='w+') as df:
            df.write(sha256_digest)

        return
    
    def deploy_zip_package_via_ssh(self, agent: SshAgent, package_name: str, destination: str):

        package_name = package_name.strip()
        if not package_name.endswith(".zip"):
            package_name = f"{package_name}.zip"

        destination = destination.strip()

        status, stdout, stderr = agent.run_cmd('echo "~"')
        if status != 0:
            errmsg = "Unable to obtain remote home directory for client."
            raise Exception(errmsg)
        
        rmt_home = stdout.strip()
        if destination.startswith("~"):
            destination = destination.replace("~", rmt_home)

        lcl_filename = os.path.join(self._cache_dir, package_name)
        rmt_filename = os.path.join(destination, package_name)

        agent.file_push(lcl_filename, rmt_filename)

        unzip_command = f"unzip -d {destination} {rmt_filename}"
        status, stdout, stderr = agent.run_cmd(unzip_command)
        if status != 0:
            errmsg_lines = [
                "Unable to unzip the package archive on the remote client.",
                f"STDERR: {stderr}"
            ]
            errmsg = os.linesep.join(errmsg_lines)
            raise RuntimeError(errmsg)

        setup_command = f"{destination}/development/setup-environment reset"
        status, stdout, stderr = agent.run_cmd(setup_command)
        if status != 0:
            errmsg_lines = [
                "Unable to setup the remote automation environment on the remote client.",
                f"STDERR: {stderr}"
            ]
            errmsg = os.linesep.join(errmsg_lines)
            raise RuntimeError(errmsg)

        return
