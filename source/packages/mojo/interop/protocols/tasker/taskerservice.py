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


from typing import Optional

import logging
import os

from logging.handlers import WatchedFileHandler
from collections import OrderedDict
from uuid import uuid4

import rpyc

from mojo.xmods.ximport import import_by_name
from mojo.interop.protocols.tasker.taskingresult import TaskingResult, TaskingResultPromise
from mojo.interop.protocols.tasker.taskeraspects import TaskerAspects

class TaskerService(rpyc.Service):
    """
        The :class:`TaskerService` is an rpyc service that handles the spawning of tasks
        on a node.
    """

    taskings = OrderedDict()
    logging_directory = None
    taskings_log_directory = None

    def __init__(self) -> None:
        super().__init__()
        self._aspects = None
        self._logging_directory = None
        self._tasking_log_directory = None
        return

    def exposed_execute_tasking(self, *, module_name: str, tasking_name: str, parent_id: Optional[str] = None,
                                aspects: Optional[TaskerAspects]=None, **kwargs) -> TaskingResultPromise:

        promise = None

        if aspects is None:
            aspects = self._aspects

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

            tasking = tasking_type(task_id=task_id, parent_id=parent_id, logfile=logfile, logger=logger, aspects=aspects)
            self.taskings[task_id] = tasking

            promise = tasking.execute(**kwargs)

        else:
            errmsg = f"The specified tasking was not found. module={module_name} tasking={tasking_name}"
            raise ValueError(errmsg)

        return promise

    def exposed_get_tasking_result(self, *, task_id) -> TaskingResult:
        return
    
    def exposed_get_tasking_status(self, *, task_id):
        return

    def exposed_set_default_aspects(self, *, aspects: TaskerAspects):
        self._aspects = aspects
        return
