
"""
.. module:: taskernode
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: The :class:`TaskerNode` object that is used to.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []
__version__ = "1.0.0"
__maintainer__ = "Myron Walker"
__email__ = "myron.walker@gmail.com"
__status__ = "Development" # Prototype, Development or Production
__license__ = "MIT"


import rpyc

from mojo.interop.protocols.tasker.taskingresult import TaskingResult

class TaskerNode:
    """
        The :class:`TaskerNode` object represents a remote tasker service endpoint.
    """

    def __init__(self, ipaddr: str, port: int):
        self._ipaddr = ipaddr
        self._port = port
        self._client = None
        return

    @property
    def ipaddr(self):
        return self._ipaddr
    
    @property
    def port(self):
        return self._port

    def execute_tasking(self, *, module_name: str, tasking_name: str, **kwargs) -> TaskingResult:

        if self._client is None:
            self._connect()

        result = self._client.root.execute_tasking(module_name=module_name, tasking_name=tasking_name, **kwargs)

        return result

    def _connect(self):
        self._client = rpyc.connect(self._ipaddr, self._port, keepalive=True)
        return
