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
import tempfile
import threading
import traceback


from collections import OrderedDict
from logging.handlers import RotatingFileHandler
from uuid import uuid4

import rpyc

from mojo.errors.exceptions import SemanticError


from mojo.results.model.progresscode import ProgressCode
from mojo.results.model.progressinfo import ProgressInfo
from mojo.results.model.resultcode import ResultCode
from mojo.results.model.taskingresult import TaskingResult

from mojo.xmods.compression import create_archive_of_folder
from mojo.xmods.fspath import expand_path
from mojo.xmods.ximport import import_by_name

from mojo.interop.protocols.tasker.taskingresultpromise import TaskingRef
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
    
    logger = None
    logging_directory = "/opt/tasker/logs"
    logging_level = logging.DEBUG

    taskings_log_directory = "/opt/tasker/logs/taskings"
    taskings_log_level = logging.DEBUG

    notify_url = None
    notify_headers = None

    def __init__(self) -> None:
        super().__init__()

        this_type = type(self)

        this_type.service_lock.acquire()
        try:
            if this_type.logger is None:
                self._reinitialize_service_logging()
        finally:
            this_type.service_lock.release()

        return


    def exposed_archive_folder(self, *, folder_to_archive: str, dest_folder: str, archive_name: str, compression_level: int = 7) -> str:

        this_type = type(self)

        this_type.logger.info("Method 'exposed_archive_folder' was called.")

        if not archive_name.endswith(".zip"):
            archive_name = f"{archive_name}.zip"

        folder_to_archive = expand_path(folder_to_archive)

        if not os.path.exists(folder_to_archive):
            raise FileNotFoundError(f"The folder to archive folder={folder_to_archive} does not exist")

        dest_folder = expand_path(dest_folder)
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

        archive_full = os.path.join(dest_folder, archive_name)

        create_archive_of_folder(folder_to_archive, archive_full, compression_level=compression_level)

        return archive_full


    def exposed_dispose_tasking(self, *, tasking_id):

        this_type = type(self)

        this_type.logger.info("Method 'exposed_dispose_tasking' was called.")

        this_type.service_lock.acquire()
        try:
            if tasking_id in this_type.taskings:

                task: Tasking = this_type.taskings[tasking_id]
                del this_type.taskings[tasking_id]

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

        this_type.logger.info("Method 'exposed_execute_tasking' was called.")

        try:
            taskref = None

            if aspects is None:
                aspects = this_type.aspects

            # Make sure the requested "Tasking" actually exists before we attempt to instantiate one in a remote
            # process.
            module = import_by_name(module_name)

            if hasattr(module, tasking_name):

                tasking_type = getattr(module, tasking_name)

                tasking_id = str(uuid4())

                log_dir = None
                log_file = None
                log_level = this_type.taskings_log_level

                prefix = "tasking"

                if this_type.taskings_log_directory is not None:

                    taskings_log_directory = this_type.taskings_log_directory
                    if not os.path.exists(taskings_log_directory):
                        os.makedirs(taskings_log_directory)

                    prefix = tasking_type.PREFIX

                    log_dir = os.path.join(taskings_log_directory, f"{prefix}-{tasking_id}")
                    if not os.path.exists(log_dir):
                        os.makedirs(log_dir)

                    log_file = os.path.join(log_dir, f"tasking-{tasking_id}.log")


                taskref = TaskingRef(module_name, tasking_id, tasking_name, log_dir)

                # Create an instance of a TaskingManager to manage the remote process, we will manage the scope
                # if this instance by delegating it to a thread that will execute the task and monitor its lifespan
                mpctx = multiprocessing.get_context("spawn")
                tasking_manager = TaskingManager(ctx=mpctx)
                tasking_manager.start()

                tasking = tasking_manager.instantiate_tasking(module_name, tasking_name, tasking_id, parent_id, log_dir,
                    log_file, log_level, this_type.notify_url, this_type.notify_headers, aspects=aspects)

                this_type.service_lock.acquire()
                try:
                    this_type.statuses[tasking_id] = str(ProgressCode.NotStarted.value)
                    this_type.taskings[tasking_id] = tasking
                finally:
                    this_type.service_lock.release()

                sgate = threading.Event()
                sgate.clear()

                dargs = (sgate, tasking_manager, tasking, tasking_name, tasking_id, prefix, parent_id, kwargs, aspects)

                # We have to dispatch the task with a thread, because we need to leave a local thread running
                # to monitor the progress of the task.
                taskthread = threading.Thread(target=self.dispatch_task, args=dargs, daemon=True)
                taskthread.start()
        
                sgate.wait()

            else:
                errmsg = f"The specified tasking 'module' was not found. module={module_name} tasking={tasking_name}"
                raise ValueError(errmsg)
        except:
            errmsg = traceback.format_exc()
            this_type.logger.error(errmsg)
            raise

        return taskref.as_dict()


    def exposed_file_exists(self, *, filename) -> str:

        filename = expand_path(filename)

        exists = False

        if os.path.exists(filename) and os.path.isfile(filename):
            exists = True

        return exists
    

    def exposed_file_exists(self, *, folder) -> str:

        folder = expand_path(folder)

        exists = False

        if os.path.exists(folder) and os.path.isdir(folder):
            exists = True

        return exists


    def exposed_get_tasking_result(self, *, tasking_id) -> TaskingResult:

        this_type = type(self)

        this_type.logger.info("Method 'exposed_get_tasking_result' was called.")

        result = None

        this_type.service_lock.acquire()
        try:
            if tasking_id in this_type.results:
                result = this_type.results[tasking_id]
            else:
                if tasking_id in this_type.taskings:
                    tstatus = this_type.statuses[tasking_id]
                    
                    if not (tstatus == ProgressCode.Completed or tstatus == ProgressCode.Errored or tstatus == ProgressCode.Failed):
                        errmsg = f"The task for tasking_id='{tasking_id}' is not in a completed state. The results are not yet available."
                        raise SemanticError(errmsg)
                else:
                    errmsg = f"The specified tasking tasking_id={tasking_id} is not known to this TaskerService instance."
                    raise ValueError(errmsg)
        finally:
            this_type.service_lock.release()

        result_str = pickle.dumps(result)

        return result_str
    
    def exposed_get_tasking_status(self, *, tasking_id):

        this_type = type(self)

        this_type.logger.info("Method 'exposed_get_tasking_status' was called.")

        tstatus = None

        this_type.service_lock.acquire()
        try:
            if tasking_id in this_type.statuses:
                tstatus = str(this_type.statuses[tasking_id])
        finally:
            this_type.service_lock.release()

        return tstatus
    
    def exposed_has_completed_and_result_ready(self, *, tasking_id):

        complete_and_ready = False

        this_type = type(self)

        this_type.logger.info("Method 'exposed_has_completed_and_result_ready' was called.")

        this_type.service_lock.acquire()
        try:
            if tasking_id in this_type.statuses:
                tstatus = str(this_type.statuses[tasking_id])

                if tstatus == ProgressCode.Completed or tstatus == ProgressCode.Errored or tstatus == ProgressCode.Failed:
                    if tasking_id in this_type.results:
                        complete_and_ready = True

        finally:
            this_type.service_lock.release()

        return complete_and_ready


    def exposed_make_folder(self, *, folder: str):

        folder = expand_path(folder)

        os.makedirs(folder)

        return


    def exposed_reinitialize_logging(self, *, logging_directory: Optional[str] = None,
                                     logging_level: Optional[int] = None,
                                     taskings_log_directory: Optional[str] = None,
                                     taskings_log_level: Optional[int] = logging.DEBUG):

        if taskings_log_directory is None:
            taskings_log_directory = logging_directory
        if taskings_log_level is None:
            taskings_log_level = logging_level

        this_type = type(self)

        this_type.logger.info("Method 'exposed_reinitialize_logging' was called.")

        this_type.service_lock.acquire()
        try:
            reinitialize_service_logging = False

            if logging_directory is not None:
                this_type.logging_directory = expand_path(logging_directory)
                reinitialize_service_logging = True

            if logging_level is not None:
                this_type.logging_level = expand_path(logging_level)
                reinitialize_service_logging = True

            if reinitialize_service_logging:
                self._reinitialize_service_logging()

            if taskings_log_directory is not None:
                this_type.taskings_log_directory = expand_path(taskings_log_directory)
            if taskings_log_level is not None:
                this_type.taskings_log_level = expand_path(taskings_log_level)
        finally:
            this_type.service_lock.release()
        
        return


    def exposed_resolve_path(self, *, path) -> str:

        path = expand_path(path)

        return path


    def exposed_set_notify_parameters(self, *, notify_url: str, notify_headers: dict):

        this_type = type(self)

        this_type.logger.info("Method 'exposed_set_notify_parameters' was called.")

        this_type.service_lock.acquire()
        try:
            this_type.notify_url = notify_url
            this_type.notify_headers = notify_headers
        finally:
            this_type.service_lock.release()
        
        return
    
    def dispatch_task(self, sgate: threading.Event, tasking_manager: TaskingManager, tasking: Tasking,
                      tasking_name: str, tasking_id: str, prefix: str, parent_id: str, kwparams: dict, 
                      aspects: TaskerAspects):

        this_type = type(self)

        # Notify the thread starting us that we have started.
        sgate.set()
        del sgate

        this_type.logger.info(f"Dispatching task_type={tasking_name} id={tasking_id}")

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

                        if len(result.errors) > 0:
                            this_type.statuses[tasking_id] = str(ProgressCode.Errored.value)
                        elif len(result.failures) > 0:
                            this_type.statuses[tasking_id] = str(ProgressCode.Failed.value)
                        else:
                            this_type.statuses[tasking_id] = str(ProgressCode.Completed.value)

                        this_type.results[tasking_id] = result
                        break

                    prog_status = str(progress.status.value)
                    this_type.statuses[tasking_id] = prog_status

                finally:
                    this_type.service_lock.release()

        except:
            tresult = TaskingResult(tasking_id, tasking.full_name, parent_id, ResultCode.ERRORED, prefix=prefix)
            this_type.statuses[tasking_id] = str(ProgressCode.Errored.value)
            this_type.results[tasking_id] = tresult

            tb_msg = traceback.format_exc()
            this_type.logger.error(tb_msg)
            raise

        finally:
            tasking_manager.shutdown()

        return

    def _reinitialize_service_logging(self):

        this_type = type(self)

        if this_type.logger is None:
            this_type.logger = logging.getLogger()
        
        handlers_list = [h for h in this_type.logger.handlers]

        for handler in handlers_list:
            this_type.logger.removeHandler(handler)

        logging_dir = this_type.logging_directory
        if not os.path.exists(logging_dir):
            try:
                logging_dir = os.makedirs(logging_dir)
            except:
                logging_dir = tempfile.mkdtemp()
                this_type.logging_directory = logging_dir

        log_file = os.path.join(logging_dir, "tasker-server.log")

        rotating_handler = RotatingFileHandler(log_file, maxBytes=8000, backupCount=10)
        rotating_handler.setLevel(this_type.logging_level)

        this_type.logger.addHandler(rotating_handler)

        return