"""
.. module:: taskersession
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`TaskerSession` class which is used to
               store the tasking data associated with a session.

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


from typing import Dict, Optional, TYPE_CHECKING

import logging
import multiprocessing
import multiprocessing.context
import os
import pickle
import threading

from collections import OrderedDict
from datetime import datetime
from uuid import uuid4

import rpyc

from mojo.errors.exceptions import SemanticError

from mojo.errors.xtraceback import (
    create_traceback_detail,
    format_traceback_detail
)

from mojo.results.model.progresscode import ProgressCode
from mojo.results.model.progressinfo import ProgressInfo
from mojo.results.model.resultcode import ResultCode
from mojo.results.model.taskingresult import TaskingResult

from mojo.xmods.ximport import import_by_name

from mojo.interop.protocols.tasker.taskingresultpromise import TaskingRef
from mojo.interop.protocols.tasker.taskeraspects import TaskerAspects, DEFAULT_TASKER_ASPECTS
from mojo.interop.protocols.tasker.tasking import Tasking, TaskingManager

if TYPE_CHECKING:
    from mojo.interop.protocols.tasker.taskerservice import TaskerService

class TaskerSession:

    def __init__(self, service_class: "TaskerService", worker_name: str, output_directory: str, log_level: int,
                 notify_url: str = None, notify_headers: Dict[str, str] = None,
                 aspects: TaskerAspects = DEFAULT_TASKER_ASPECTS):

        self._service_class = service_class

        self._worker_name = worker_name
        self._output_directory = os.path.abspath(os.path.expandvars(os.path.expanduser(output_directory)))

        self._log_level = log_level

        self._notify_url = notify_url
        self._notify_headers = notify_headers

        self._aspects = aspects

        self._session_id = str(uuid4())

        self._start = datetime.now()
        self._last_activity = datetime.now()

        self._taskings = OrderedDict()
        self._results = OrderedDict()
        self._statuses = OrderedDict()

        self._session_lock = threading.Lock()

        return
    
    @property
    def aspects(self): 
        return self._aspects
    
    @property
    def last_activity(self) -> datetime: 
        return self._last_activity

    @property
    def output_directory(self):
        return self._output_directory

    @property
    def results(self) -> OrderedDict: 
        return self._results
    
    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def start(self) -> datetime: 
        return self._start
    
    @property
    def statuses(self) -> OrderedDict: 
        return self._statuses
    
    @property
    def taskings(self) -> OrderedDict: 
        return self._taskings
    
    @property
    def log_level(self) -> int:
        return self.log_level

    def dispose_tasking(self, tasking_id: str):
        
        self._session_lock.acquire()

        try:
            if tasking_id in self.taskings:

                task: Tasking = self.taskings[tasking_id]
                del self.taskings[tasking_id]

                self._session_lock.release()
                try:
                    task.shutdown()
                finally:
                    self._session_lock.acquire()
        finally:
            self._session_lock.release()

        return

    def execute_tasking(self, worker: str, module_name: str, tasking_name: str,
                               parent_id: Optional[str] = None, aspects: Optional[TaskerAspects]=None, **kwargs) -> TaskingRef:
        
        if aspects is None:
            aspects = self._aspects

        taskref: TaskingRef = None

        # Make sure the requested "Tasking" actually exists before we attempt to instantiate one in a remote
        # process.
        module = import_by_name(module_name)

        if hasattr(module, tasking_name):

            tasking_type = getattr(module, tasking_name)

            tasking_id = str(uuid4())

            log_dir = None
            
            if not os.path.exists(self._output_directory):
                os.makedirs(self._output_directory)

            prefix = tasking_type.PREFIX
            
            log_dir = os.path.join(self._output_directory, "taskings", f"{prefix}-{tasking_id}")
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            log_file: str = os.path.join(log_dir, f"tasking-{tasking_id}")

            taskref = TaskingRef(module_name, tasking_id, tasking_name, log_dir)

            # Create an instance of a TaskingManager to manage the remote process, we will manage the scope
            # if this instance by delegating it to a thread that will execute the task and monitor its lifespan
            mpctx = multiprocessing.get_context("spawn")
            tasking_manager = TaskingManager(ctx=mpctx)
            tasking_manager.start()

            tasking = tasking_manager.instantiate_tasking(worker, module_name, tasking_name, tasking_id, parent_id, self._output_directory,
                log_dir, log_file, self._log_level, self._notify_url, self._notify_headers, aspects=aspects)

            self._session_lock.acquire()
            try:
                self.statuses[tasking_id] = str(ProgressCode.NotStarted.value)
                self.taskings[tasking_id] = tasking
            finally:
                self._session_lock.release()

            sgate = threading.Event()
            sgate.clear()

            dargs = (sgate, tasking_manager, tasking, tasking_name, tasking_id, prefix,
                     parent_id, log_file, kwargs, aspects)

            # We have to dispatch the task with a thread, because we need to leave a local thread running
            # to monitor the progress of the task.
            taskthread = threading.Thread(target=self._dispatch_task, args=dargs, daemon=True)
            taskthread.start()
    
            sgate.wait()

        else:
            errmsg = f"The specified tasking 'module' was not found. module={module_name} tasking={tasking_name}"
            raise ValueError(errmsg)
    
        return taskref
    
    def get_tasking_result(self, tasking_id: str) -> str:

        self._session_lock.acquire()
        try:
            if tasking_id in self._results:
                result = self._results[tasking_id]
            else:
                if tasking_id in self._taskings:
                    tstatus = self._statuses[tasking_id]
                    
                    if not (tstatus == ProgressCode.Completed or tstatus == ProgressCode.Errored or tstatus == ProgressCode.Failed):
                        errmsg = f"The task for tasking_id='{tasking_id}' is not in a completed state. The results are not yet available."
                        raise SemanticError(errmsg)
                else:
                    errmsg = f"The specified tasking tasking_id={tasking_id} is not known to this TaskerService instance."
                    raise ValueError(errmsg)
        finally:
            self._session_lock.release()

        result_str = pickle.dumps(result)

        return result_str

    def get_tasking_status(self, tasking_id: str) -> str:

        self._session_lock.acquire()
        try:
            if tasking_id in self._statuses:
                tstatus = str(self._statuses[tasking_id])
        finally:
            self._session_lock.release()

        return tstatus

    def has_completed_and_result_ready(self, tasking_id) -> bool:

        complete_and_ready = False

        self._session_lock.acquire()
        try:
            if tasking_id in self._statuses:
                tstatus = str(self._statuses[tasking_id])

                if tstatus == ProgressCode.Completed or tstatus == ProgressCode.Errored or tstatus == ProgressCode.Failed:
                    if tasking_id in self._results:
                        complete_and_ready = True

        finally:
            self._session_lock.release()

        return complete_and_ready
    
    def shutdown(self):

        # Go through all of the tasks and if they have not completed, cancel them
        tasking_id: str
        tasking: Tasking
        tstatus: ProgressCode

        for tasking_id, tasking in self._taskings.items():
            tstatus = self._statuses[tasking_id]

            if tstatus in [ProgressCode.NotStarted, ProgressCode.Paused, ProgressCode.Running]:
                tasking.shutdown()

        return

    def _dispatch_task(self, sgate: threading.Event, tasking_manager: TaskingManager, tasking: Tasking,
                      tasking_name: str, tasking_id: str, prefix: str, parent_id: str,
                      log_file: str, kwparams: dict, aspects: TaskerAspects):

        this_type = type(self)

        # Notify the thread starting us that we have started.
        sgate.set()
        del sgate

        self._service_class.log_info(f"Dispatching task_type={tasking_name} id={tasking_id}")

        progress = None

        inactivity_timeout = aspects.inactivity_timeout

        try:
            progress_queue = tasking_manager.Queue()

            tasking.execute(progress_queue, kwparams)

            while(True):

                progress: ProgressInfo = progress_queue.get(block=True, timeout=inactivity_timeout)

                self._session_lock.acquire()
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
                    self._session_lock.release()

        except BaseException as err:
            tbdetail = create_traceback_detail(err)

            errmsg_lines = format_traceback_detail(tbdetail)
            errmsg = os.linesep.join(errmsg_lines)

            this_type.logger.error(errmsg)
            with open(log_file, "+a") as tlogf:
                tlogf.write(errmsg)
            
            tresult = TaskingResult(tasking_id, tasking.full_name, parent_id, ResultCode.ERRORED, prefix=prefix)
            this_type.statuses[tasking_id] = str(ProgressCode.Errored.value)
            tresult.add_error(tbdetail)
            this_type.results[tasking_id] = tresult

            raise

        finally:
            tasking_manager.shutdown()

        return

