
from typing import Generator

from mojo import testplus

from mojo.landscaping.landscape import Landscape
from mojo.landscaping.includefilters import IncludeDeviceByDeviceType

from mojo.interop.clients.linux.linuxclient import LinuxClient

@testplus.resource()
def each_client(lscape: Landscape, constraints={}) -> Generator[LinuxClient, None, None]:
    
    includes = [IncludeDeviceByDeviceType("network/client-linux")]

    client_list = lscape.get_devices(include_filters=includes)

    for client in client_list:
        yield client


@testplus.param(each_client, identifier="client")
def test_ssh_say_hello(client: LinuxClient):

    cmd = "echo 'Hello'"

    status, stdout, stderr = client.ssh.run_cmd(cmd)
    testplus.assert_equal(stdout.strip(), "Hello")

    return
