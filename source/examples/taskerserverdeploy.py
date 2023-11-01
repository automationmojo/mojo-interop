
from mojo.interop.protocols.ssh.sshagent import SshAgent
from mojo.xmods.credentials.sshcredential import SshCredential

from mojo.interop.clients.clientsourcepackager import ClientSourcePackager

def tasker_server_deploy():

    sshcred = SshCredential(identifier="pi-user", categories=["ssh"], role="taskerserver", username="pi", password="")

    client_addr = "192.168.1.175"

    agent = SshAgent(client_addr, sshcred)

    source_root = "~/repos/testplus"
    cache_dir = "~/repos/testplus/.cache"
    package_name = "testplus_package.zip"

    packager = ClientSourcePackager(source_root, cache_dir)

    packager.create_zip_package("testplus_package.zip")

    packager.deploy_zip_package_via_ssh(agent, package_name, "~/repos/testplus")

    return


if __name__ == "__main__":
    tasker_server_deploy()
