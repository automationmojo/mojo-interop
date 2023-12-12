
from mojo import testplus

from mojo.coupling.factories import create_landscape, create_linux_client_coordinator_coupling

testplus.originate_parameter(create_linux_client_coordinator_coupling, identifier="lc_coupling")

testplus.originate_parameter(create_landscape, identifier='lscape')
