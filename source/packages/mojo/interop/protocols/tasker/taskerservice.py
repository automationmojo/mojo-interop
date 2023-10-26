"""
.. module:: taskerservice
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`TaskerService` class which is an rypc service
               for running and monitoring remote tasks.

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


from typing import Any, Optional, Type, Union

import logging
import os
import threading

from logging.handlers import WatchedFileHandler
from collections import OrderedDict
from uuid import uuid4

import rpyc

from mojo.errors.exceptions import SemanticError
from mojo.xmods.ximport import import_by_name
from mojo.interop.protocols.tasker.taskingresult import TaskingResult, TaskingStatus, TaskingRef
from mojo.interop.protocols.tasker.taskeraspects import TaskerAspects
from mojo.interop.protocols.tasker.tasking import Tasking

class TaskerService(rpyc.Service):
    """
        The :class:`TaskerService` is an rpyc service that handles the spawning of tasks
        on a node.
    """

    service_lock = threading.Lock()

    taskings = OrderedDict()
    logging_directory = None
    taskings_log_directory = None

    def __init__(self) -> None:
        super().__init__()
        self._aspects = None
        self._logging_directory = None
        self._tasking_log_directory = None
        self._notify_url = None
        self._notify_headers = None
        return

    def exposed_dispose_tasking(self, *, task_id):

        self.service_lock.acquire()
        try:
            if task_id in self.taskings:

                task: Tasking = self.taskings[task_id]
                del self.taskings[task_id]

                self.service_lock.release()
                try:
                    task.effect_shutdown()
                finally:
                    self.service_lock.acquire()

        finally:
            self.service_lock.release()

        return

    def exposed_execute_tasking(self, *, module_name: str, tasking_name: str, parent_id: Optional[str] = None,
                                aspects: Optional[TaskerAspects]=None, **kwargs) -> dict:

        taskref = None

        module = import_by_name(module_name)

        if hasattr(module, tasking_name):
            tasking_type = getattr(module, tasking_name)

            task_id = str(uuid4())
            logger = None

            logfile = None
            if self.taskings_log_directory is not None:
                logfile = os.path.join(self.taskings_log_directory, f"tasking-{task_id}.log")

                log_handler = WatchedFileHandler(logfile)
                logging.basicConfig(format=logging.BASIC_FORMAT, level=logging.DEBUG, handlers=[log_handler])
                
                logger = logging.getLogger("tasker-server")

            taskref = TaskingRef(module_name, task_id, tasking_name, logfile)

            tasking: Tasking = tasking_type(task_id=task_id, parent_id=parent_id, notify_url=self._notify_url,
                                            notify_headers=self._notify_headers, logfile=logfile, logger=logger,
                                            aspects=aspects)
            self.taskings[task_id] = tasking

            sgate = threading.Event()
            sgate.clear()

            dargs = (sgate, tasking, aspects, kwargs)

            # We have to dispatch the task with a thread, because we need to leave a local thread running
            # to monitor the progress of the task.
            taskthread = threading.Thread(target=self.dispatch_task, args=dargs, daemon=True)
            taskthread.start()
    
            sgate.wait()

        else:
            errmsg = f"The specified tasking 'module' was not found. module={module_name} tasking={tasking_name}"
            raise ValueError(errmsg)

        return taskref.as_dict()

    def exposed_get_tasking_result(self, *, task_id) -> TaskingResult:

        result = None

        self.service_lock.acquire()
        try:
            if task_id in self.taskings:
                task: Tasking = self.taskings[task_id]

                if task.task_status == TaskingStatus.Completed or task.task_status == TaskingStatus.Errored:
                    result = task.result
                else:
                    errmsg = f"The task '{task.task_status}' is not in a completed state. Result not yet available"
                    raise SemanticError(errmsg)
        finally:
            self.service_lock.release()


        return result
    
    def exposed_get_tasking_status(self, *, task_id):

        tstatus = None

        self.service_lock.acquire()
        try:
            if task_id in self.taskings:
                task: Tasking = self.taskings[task_id]

                tstatus = task.task_status
        finally:
            self.service_lock.release()

        return tstatus

    def exposed_set_notify_parameters(self, *, notify_url: str, notify_headers: dict):
        self._notify_url = notify_url
        self._notify_headers = notify_headers
        return
    
    def dispatch_task(self, sgate: threading.Event, tasking: Tasking, aspects: Union[TaskerAspects, None], kwparams: dict):

        # Notify the thread starting us that we have started.
        sgate.set()
        del sgate

        promise = tasking.execute(kwparams, aspects=aspects)
        
        return
