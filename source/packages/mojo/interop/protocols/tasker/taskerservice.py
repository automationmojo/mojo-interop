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
import multiprocessing
import multiprocessing.context
import os
import pickle
import threading


from collections import OrderedDict
from uuid import uuid4

import rpyc

from mojo.errors.exceptions import SemanticError


from mojo.results.model.progresscode import ProgressCode
from mojo.results.model.progressinfo import ProgressInfo

from mojo.xmods.ximport import import_by_name

from mojo.interop.protocols.tasker.taskingresult import TaskingResult, TaskingRef
from mojo.interop.protocols.tasker.taskeraspects import TaskerAspects, DEFAULT_TASKER_ASPECTS
from mojo.interop.protocols.tasker.tasking import Tasking, TaskingManager


class TaskerService(rpyc.Service):
    """
        The :class:`TaskerService` is an rpyc service that handles the spawning of tasks
        on a node.
    """

    service_lock = threading.Lock()

    initialized = False

    taskings = OrderedDict()
    results = OrderedDict()
    statuses = OrderedDict()

    aspects = DEFAULT_TASKER_ASPECTS
    
    logger = logging.getLogger()
    logging_directory = None
    logging_level = logging.DEBUG

    taskings_log_directory = None
    taskings_log_level = logging.DEBUG

    notify_url = None
    notify_headers = None

    def __init__(self) -> None:
        super().__init__()
        return

    def exposed_dispose_tasking(self, *, task_id):

        this_type = type(self)

        this_type.service_lock.acquire()
        try:
            if task_id in this_type.taskings:

                task: Tasking = this_type.taskings[task_id]
                del this_type.taskings[task_id]

                this_type.service_lock.release()
                try:
                    task.shutdown()
                finally:
                    this_type.service_lock.acquire()

        finally:
            this_type.service_lock.release()

        return

    def exposed_execute_tasking(self, *, module_name: str, tasking_name: str, parent_id: Optional[str] = None,
                                aspects: Optional[TaskerAspects]=None, **kwargs) -> dict:

        this_type = type(self)

        taskref = None

        if aspects is None:
            aspects = this_type.aspects

        # Make sure the requested "Tasking" actually exists before we attempt to instantiate one in a remote
        # process.
        module = import_by_name(module_name)

        if hasattr(module, tasking_name):

            task_id = str(uuid4())

            log_dir = None
            log_file = None
            log_level = this_type.taskings_log_level

            if this_type.taskings_log_directory is not None:

                taskings_log_directory = this_type.taskings_log_directory
                if not os.path.exists(taskings_log_directory):
                    os.makedirs(taskings_log_directory)

                log_dir = os.path.join(taskings_log_directory, f"tasking-{task_id}")
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)

                log_file = os.path.join(log_dir, f"tasking-{task_id}.log")


            taskref = TaskingRef(module_name, task_id, tasking_name, log_dir)

            # Create an instance of a TaskingManager to manage the remote process, we will manage the scope
            # if this instance by delegating it to a thread that will execute the task and monitor its lifespan
            mpctx = multiprocessing.get_context("spawn")
            tasking_manager = TaskingManager(ctx=mpctx)
            tasking_manager.start()

            tasking = tasking_manager.instantiate_tasking(module_name, tasking_name, task_id, parent_id, log_dir,
                log_file, log_level, this_type.notify_url, this_type.notify_headers, aspects=aspects)

            this_type.service_lock.acquire()
            try:
                this_type.taskings[task_id] = tasking
            finally:
                this_type.service_lock.release()

            sgate = threading.Event()
            sgate.clear()

            dargs = (sgate, tasking_manager, tasking, task_id, kwargs, aspects)

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

        this_type = type(self)

        result = None

        this_type.service_lock.acquire()
        try:
            if task_id in this_type.results:
                result = this_type.results[task_id]
            else:
                if task_id in this_type.taskings:
                    tstatus = this_type.statuses[task_id]
                    
                    if not (tstatus == ProgressCode.Completed or tstatus == ProgressCode.Errored):
                        errmsg = f"The task for task_id='{task_id}' is not in a completed state. The results are not yet available."
                        raise SemanticError(errmsg)
                else:
                    errmsg = f"The specified tasking task_id={task_id} is not known to this TaskerService instance."
                    raise ValueError(errmsg)
        finally:
            this_type.service_lock.release()

        result_str = pickle.dumps(result)

        return result_str
    
    def exposed_get_tasking_status(self, *, task_id):

        this_type = type(self)

        tstatus = None

        this_type.service_lock.acquire()
        try:
            if task_id in this_type.statuses:
                tstatus = str(this_type.statuses[task_id])
        finally:
            this_type.service_lock.release()

        return tstatus

    def exposed_reinitialize_logging(self, *, logging_directory: str, logging_level: int,
                                     taskings_log_directory: Optional[str] = None,
                                     taskings_log_level: Optional[int] = logging.DEBUG):

        if taskings_log_directory is None:
            taskings_log_directory = logging_directory
        if taskings_log_level is None:
            taskings_log_level = logging_level

        this_type = type(self)

        this_type.service_lock.acquire()
        try:

            this_type.logging_directory = logging_directory
            this_type.logging_level = logging_level
            this_type.taskings_log_directory = taskings_log_directory
            this_type.taskings_log_level = taskings_log_level
        finally:
            this_type.service_lock.release()
        
        return

    def exposed_set_notify_parameters(self, *, notify_url: str, notify_headers: dict):

        this_type = type(self)

        this_type.service_lock.acquire()
        try:
            this_type.notify_url = notify_url
            this_type.notify_headers = notify_headers
        finally:
            this_type.service_lock.release()
        
        return
    
    def dispatch_task(self, sgate: threading.Event, tasking_manager: TaskingManager, tasking: Tasking,
                      task_id: str, kwparams: dict, aspects: TaskerAspects):

        this_type = type(self)

        # Notify the thread starting us that we have started.
        sgate.set()
        del sgate

        progress = None

        inactivity_timeout = aspects.inactivity_timeout

        try:
            progress_queue = tasking_manager.Queue()

            tasking.execute(progress_queue, kwparams)

            while(True):

                progress: ProgressInfo = progress_queue.get(block=True, timeout=inactivity_timeout)

                this_type.service_lock.acquire()
                try:

                    if isinstance(progress, TaskingResult):
                        result: TaskingResult = progress

                        if result.exception is not None:
                            this_type.statuses[task_id] = str(ProgressCode.Errored.value)
                        else:
                            this_type.statuses[task_id] = str(ProgressCode.Completed.value)

                        this_type.results[task_id] = result
                        break

                    prog_status = str(progress.status.value)
                    this_type.statuses[task_id] = prog_status

                finally:
                    this_type.service_lock.release()

        finally:
            tasking_manager.shutdown()

        return
