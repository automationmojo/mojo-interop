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



from typing import Optional,  Tuple

import os
import socket
import tempfile
import logging
import threading

from logging.handlers import WatchedFileHandler
from rpyc.utils.server import ThreadedServer


from mojo.interop.protocols.tasker.taskerservice import TaskerService


TASKER_PROTOCOL_CONFIG = {
    "allow_public_attrs": True,
    "allow_pickle": True,
    "import_custom_exceptions": True,
    "allow_custom_exceptions": True,
    "sync_request_timeout": 60,
    "logger": logging.getLogger()
}

class TaskerServer(ThreadedServer):
    """
        The :class:`TaskerServer` starts an RPyC server in an internal thread that is capable of handling
        requests for tasking. 
    """
    
    TASKER_SERVICE_PORT = 8686


    def __init__(self, hostname=None, ipv6=False, port=TASKER_SERVICE_PORT,
                 backlog=socket.SOMAXCONN, reuse_addr=True, authenticator=None, registrar=None,
                 auto_register=None, protocol_config=TASKER_PROTOCOL_CONFIG, logging_directory: Optional[str]=None,
                 listener_timeout=0.5, socket_path=None):
        
        if logging_directory is None:
            logging_directory = tempfile.mkdtemp(prefix=f"taskerserver-{os.getpid()}-")

        TaskerService.logging_directory = logging_directory
        TaskerService.taskings_log_directory = os.path.join(logging_directory, f"taskings")

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


    def serve_forever(self):
        """
            Called when the taskerserver is run from the main thread of a service instance.
        """
        
        self._service_thread_entry()

        return


    def _service_thread_entry(self, start_gate: Optional[threading.Event] = None):
        
        # If we were passed a start_gate, it means a thread is waiting for
        # us to kick off.  Set the start_gate to indicate we are running in
        # a new thread
        if start_gate is not None:
            start_gate.set()

        self.logger.info("Service thread starting ...")

        self._listen()
        self._register()
        try:

            while self.active:
                self.accept()

        except EOFError:
            pass  # server closed by another thread
        except KeyboardInterrupt:
            print("")
            self.logger.info("keyboard interrupt!")
        finally:
            self.logger.info("Service thread terminating ...")
            self.close()

        return

