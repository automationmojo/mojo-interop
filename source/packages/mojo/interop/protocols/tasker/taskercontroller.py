"""
.. module:: taskercontroller
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: The :class:`TaskerController` package contains the controller object used to create a distributed
               network of :class:`TaskerService` objects.

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


from typing import List, Optional, Type, Union


import logging
import os
import time


from datetime import datetime, timedelta

from mojo.errors.exceptions import NotOverloadedError, SemanticError

from mojo.results.model.taskingresult import TaskingResult
from mojo.results.model.progressdelivery import SummaryProgressDelivery


from mojo.interop.protocols.tasker.taskeraspects import TaskerAspects, DEFAULT_TASKER_ASPECTS
from mojo.interop.protocols.tasker.tasking import Tasking, TaskingIdentity
from mojo.interop.protocols.tasker.taskernode import TaskerNode, TaskerClientNode
from mojo.interop.protocols.tasker.taskingresultpromise import TaskingResultPromise
from mojo.interop.protocols.tasker.taskerservice import TaskerService
from mojo.interop.protocols.tasker.taskerservermanager import TaskerServerManager, spawn_tasking_server_process

from mojo.landscaping.client.clientbase import ClientBase


TASKER_PORT = 8686

class TaskerController:
    """
        The :class:`TaskerController` object lets you startup and control task processing across
        a collection of clients.
    """

    def __init__(self, logging_directory: Optional[str] = None,
                 aspects: Optional[TaskerAspects] = DEFAULT_TASKER_ASPECTS):
        self._logging_directory = logging_directory
        self._aspects = aspects

        self._tasker_nodes: List[TaskerNode] = []
        self._network_started = False
        return

    @property
    def tasker_clients(self) -> List[ClientBase]:
        clients = [ tn.client for tn in self._tasker_nodes]
        return clients

    @property
    def tasker_nodes(self):
        return self._tasker_nodes


    def execute_tasking_on_all_nodes(self, *, tasking: Union[TaskingIdentity, Type[Tasking]], parent_id: str = None,
                                     aspects: Optional[TaskerAspects] = None, **kwargs) -> List[TaskingResultPromise]:

        if aspects is None:
            aspects = self._aspects

        promise_list = []

        if not isinstance(tasking, TaskingIdentity):
            tasking = tasking.get_identity()
        module_name, tasking_name = tasking.as_tuple()

        for node in self._tasker_nodes:
            promise = node.execute_tasking(module_name=module_name, tasking_name=tasking_name, parent_id=parent_id, aspects=aspects, **kwargs)
            promise_list.append(promise)

        return promise_list

    def execute_tasking_on_node(self, node: TaskerNode, *, tasking: Union[TaskingIdentity, Type[Tasking]], parent_id: str = None,
                                aspects: Optional[TaskerAspects] = None, **kwargs) -> TaskingResultPromise:

        if aspects is None:
            aspects = self._aspects

        promise = None

        if not isinstance(tasking, TaskingIdentity):
            tasking = tasking.get_identity()
        module_name, tasking_name = tasking.as_tuple()
        
        promise = node.execute_tasking(module_name=module_name, tasking_name=tasking_name, parent_id=parent_id, aspects=aspects, **kwargs)

        return promise

    def execute_tasking_on_node_list(self, node_list: List[TaskerNode], *, tasking: Union[TaskingIdentity, Type[Tasking]], parent_id: str = None,
                                     aspects: Optional[TaskerAspects] = None, **kwargs) -> List[TaskingResultPromise]:

        if aspects is None:
            aspects = self._aspects

        promise_list = []

        if not isinstance(tasking, TaskingIdentity):
            tasking = tasking.get_identity()
        module_name, tasking_name = tasking.as_tuple()

        for node in node_list:
            promise = node.execute_tasking(module_name=module_name, tasking_name=tasking_name, parent_id=parent_id, aspects=aspects, **kwargs)
            promise_list.append(promise)

        return promise_list

    def reinitialize_logging_on_nodes(self, *, logging_directory: Optional[str] = None,
                                      logging_level: Optional[int] = None,
                                      taskings_log_directory: Optional[str] = None,
                                      taskings_log_level: Optional[int] = None):

        for node in self._tasker_nodes:
            node.reinitialize_logging(logging_directory=logging_directory, logging_level=logging_level,
                                      taskings_log_directory=taskings_log_directory, taskings_log_level=taskings_log_level)

        return

    def start_tasker_network(self):
        """
        """
        raise NotOverloadedError("The 'start_task_network' method must be overloaded.")

    def stop_tasker_network(self):

        raise NotOverloadedError("The 'stop_tasker_network' method must be overloaded.")

    def wait_for_tasking_results(self, promises: List[TaskingResultPromise],
                                 summary_progress: Optional[SummaryProgressDelivery] = None,
                                 aspects: Optional[TaskerAspects] = None) -> List[TaskingResult]:
        """
            This is a special wait function that checks all tasks in a list of promises to see if they 
            are complete, without blocking on a single task.  It also can poll for progress and report
            progress of the tasks if a summary_progress parameter is provided.
        """

        if aspects is None:
            aspects = self._aspects

        progress_callback = None
        progress_interval = None
        
        if summary_progress is not None:
            progress_callback = summary_progress.progress_callback
            progress_interval = summary_progress.progress_interval

        if aspects is None:
            aspects = self._aspects

        # We should always have a completion_timeout and completion_interval, if we don't
        # something is wrong
        timeout = aspects.completion_timeout
        interval = aspects.completion_interval

        now_time = datetime.now()
        start_time = now_time
        end_time = start_time + timedelta(seconds=timeout)

        next_progress = None
        if summary_progress is not None:
            next_progress = start_time + timedelta(seconds=progress_interval)

        
        wait_on = [ np for np in promises ]
        not_ready = []

        while True:

            # Loop through our promises and check the status of the results
            while len(wait_on) > 0:
                np = wait_on.pop()
                completed = np.is_task_complete()
                if not completed:
                    not_ready.append(np)

            if len(not_ready) == 0:
                # We are done, every tasking is completed
                break
            else:
                # Reset our wait lists so we can circle back
                # after a short word from our sponsers
                wait_on = [p for p in not_ready]
                not_ready = []

            now_time = datetime.now()
            if now_time > end_time:
                err_msg_lines = [
                    "Timeout: Waiting for taskings to complete."
                ]
                errmsg = os.linesep.join(err_msg_lines)
                raise TimeoutError(errmsg)

            interval_remaining = interval

            # Treat our progress retrieval time as being part of our
            # interval between checks for completion.
            if next_progress is not None:
                if now_time > next_progress:
                    progress_list = []
                    before_progress = time.time()

                    # Collect the progress
                    for p in promises:
                        progress = p.get_progress()
                        progress_list.append(progress)
                    
                    # Report the list of progress reports
                    progress_callback(progress_list)

                    after_progress = time.time()
                    interval_remaining = interval_remaining - (after_progress - before_progress)

            if interval_remaining > 0:
                time.sleep(interval_remaining)


        # If we made it here, we didn't timeout, that means we should
        # have a result from each tasking in our promise objects
        results = []
        for np in promises:
            nxtres = np.get_result()
            results.append(nxtres)

        return results


class ProcessTaskerController(TaskerController):

    def __init__(self, logging_directory: Optional[str] = None, aspects: Optional[TaskerAspects] = DEFAULT_TASKER_ASPECTS):
        super().__init__(logging_directory=logging_directory, aspects=aspects)

        self._svr_manager: List[TaskerServerManager] = []
        self._svr_proxies: List[TaskerService] = []
        return

    def start_tasker_network(self, node_count=5, output_directory: Optional[str] = None, log_level: Optional[int] = logging.DEBUG):
        """
        """

        if self._network_started:
            errmsg = "A task network has already been started."
            raise SemanticError(errmsg)

        self._network_started = True

        for _ in range(node_count):
            svr_mgr, tasking_svr_proxy = spawn_tasking_server_process(('0.0.0.0', 0), logging_directory=self._logging_directory)

            tasking_svr_proxy.start()

            self._svr_manager.append(svr_mgr)
            self._svr_proxies.append(tasking_svr_proxy)

            ipaddr, port = tasking_svr_proxy.get_service_endpoint()
            worker_name = f"{ipaddr}: {port}"

            node = TaskerNode(ipaddr=ipaddr, port=port)
            
            node.session_open(worker_name=worker_name, output_directory=output_directory, log_level=log_level, aspects=self._aspects)

            self._tasker_nodes.append(node)

        return
    
    def stop_tasker_network(self):

        for node in self._tasker_nodes:
            node.session_close()

        return


class ClientTaskerController(TaskerController):

    def __init__(self, logging_directory: Optional[str] = None, aspects: Optional[TaskerAspects] = None):
        super().__init__(logging_directory=logging_directory, aspects=aspects)
        return

    def start_tasker_network(self, clients: List[ClientBase], output_directory: Optional[str] = None,
                             log_level: Optional[int] = logging.DEBUG):
        """
        """

        if self._network_started:
            errmsg = "A task network has already been started."
            raise SemanticError(errmsg)

        self._network_started = True

        for cl in clients:

            node = TaskerClientNode(client=cl, ipaddr=cl.ipaddr, port=TASKER_PORT)
            
            worker_name = cl.ipaddr

            node.session_open(worker_name=worker_name, output_directory=output_directory, log_level=log_level, aspects=self._aspects)
            
            self._tasker_nodes.append(node)

        return
    
    def stop_tasker_network(self):

        for node in self._tasker_nodes:
            node.session_close()

        return

