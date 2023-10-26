"""
.. module:: taskerserver
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`TaskerServer` class which is a host server for the
               tasker :class:`TaskerService`.

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


from typing import Optional,  Tuple

import os
import socket
import tempfile
import threading

import logging
from logging.handlers import WatchedFileHandler

import rpyc

from rpyc.utils.server import ThreadPoolServer

from mojo.interop.protocols.tasker.taskerservice import TaskerService


class TaskerServer(ThreadPoolServer):
    """
        The :class:`TaskerServer` starts an RPyC server in an internal thread that is capable of handling
        requests for tasking. 
    """
    
    def __init__(self, hostname=None, ipv6=False, port=0,
                 backlog=socket.SOMAXCONN, reuse_addr=True, authenticator=None, registrar=None,
                 auto_register=None, protocol_config=None, logging_directory: Optional[str]=None, listener_timeout=0.5,
                 socket_path=None):
        
        if logging_directory is None:
            logging_directory = tempfile.mkdtemp(prefix="taskserver-")

        if not os.path.exists(logging_directory):
            os.makedirs(logging_directory)

        log_file = os.path.join(logging_directory, 'tasker-server.log')
        log_handler = WatchedFileHandler(log_file)
        logging.basicConfig(format=logging.BASIC_FORMAT, level=logging.DEBUG, handlers=[log_handler])
        
        logger = logging.getLogger("tasker-server")

        super().__init__(TaskerService, hostname=hostname, ipv6=ipv6, port=port, backlog=backlog, reuse_addr=reuse_addr,
                         authenticator=authenticator, registrar=registrar, auto_register=auto_register,
                         protocol_config=protocol_config, logger=logger, listener_timeout=listener_timeout,
                         socket_path=socket_path)
        
        taskings_log_directory = os.path.join(logging_directory, "taskings")
        self.service.taskings_log_directory = taskings_log_directory

        if not os.path.exists(taskings_log_directory):
            os.makedirs(taskings_log_directory)

        self._server_thread = None
        return

    def get_service_endpoint(self) -> Tuple[str, int]:
        ipaddr, port = self.listener.getsockname()
        return ipaddr, port

    def start(self):
        """
            Starts the server request accept thread.
        """
        
        start_gate = threading.Event()
        start_gate.clear()

        self._server_running = True
        
        self._server_thread = threading.Thread(target=self._service_thread_entry, name='tasker', args=(start_gate,), daemon=True)
        self._server_thread.start()

        start_gate.wait()

        return
    
    def _service_thread_entry(self, start_gate: threading.Event):
        
        start_gate.set()

        self._listen()
        self._register()
        try:

            while self.active:
                self.accept()

        except EOFError:
            pass  # server closed by another thread
        except KeyboardInterrupt:
            print("")
            self.logger.warn("keyboard interrupt!")
        finally:
            self.logger.info("server has terminated")
            self.close()

        return
