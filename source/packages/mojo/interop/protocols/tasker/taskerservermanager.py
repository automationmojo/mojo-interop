"""
.. module:: taskerservermanager
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`TaskerServerManager` class which is used to create
               a remote :class:`TaskServer` process.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>

"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []



from typing import Optional, Tuple

import multiprocessing
import multiprocessing.managers

from mojo.interop.protocols.tasker.taskerserver import TaskerServer


class TaskerServerManager(multiprocessing.managers.SyncManager):
    """
        This is a process manager used for creating a :class:`TaskerServerManager`
        in a remote process that can be communicated with via a proxy.
    """


TaskerServerManager.register("TaskerServer", TaskerServer)


def spawn_tasking_server_process(svc_endpoint: Tuple[str, int], logging_directory: Optional[str] = None) -> Tuple[TaskerServerManager, TaskerServer]:
    ipaddr, port = svc_endpoint

    svr_manager = TaskerServerManager()
    svr_manager.start()

    tasking_svr_proxy = svr_manager.TaskerServer(hostname=ipaddr, port=port, logging_directory=logging_directory)

    return svr_manager, tasking_svr_proxy

