
from logging import Logger
import os
import tempfile
from typing import Optional
from mojo.interop.protocols.tasker.taskeraspects import TaskerAspects


from mojo.interop.protocols.tasker.taskercontroller import ProcessTaskerController
from mojo.interop.protocols.tasker.tasking import Tasking


class PrintTasking(Tasking):

    def __init__(self, task_id: str | None = None, parent_id: str | None = None, notify_url: str | None = None, notify_headers: dict | None = None, logfile: str | None = None, logger: Logger | None = None, aspects: TaskerAspects | None = None):
        super().__init__(task_id, parent_id, notify_url, notify_headers, logfile, logger, aspects)

        self._message = None
        self._counter = 5
        return

    def begin(self, kwparams: dict):
        super().begin(kwparams)

        self._message = kwparams["message"]
        return

    def perform(self):

        pid = os.getpid()
        print(f"({pid}) #{self._counter} {self._message}")

        morework = False
        if self._counter > 0:
            morework = True
            self._counter = self._counter - 1

        return morework


def tasking_server_example_main():

    logging_directory = tempfile.mkdtemp(prefix="taskings-")

    controller = ProcessTaskerController(logging_directory=logging_directory)
    controller.start_task_network()

    print("=============== Tasker Nodes ===============")
    for node in controller.tasker_nodes:
        print(f"    ipaddr={node.ipaddr} port={node.port} ...")

    controller.execute_task_on_all_nodes(tasking=PrintTasking, message="Hello World")

    return


if __name__ == "__main__":

    tasking_server_example_main()

