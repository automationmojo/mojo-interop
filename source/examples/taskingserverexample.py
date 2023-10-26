
import os
import tempfile
import time

from logging import Logger

from mojo.interop.protocols.tasker.taskeraspects import TaskerAspects
from mojo.interop.protocols.tasker.taskercontroller import ProcessTaskerController

from mojo.interop.protocols.tasker.taskingprogress import TaskingProgress
from mojo.interop.protocols.tasker.taskingresult import TaskingStatus
from mojo.interop.protocols.tasker.tasking import Tasking


class PrintTasking(Tasking):

    def begin(self, kwparams: dict):

        self._data = {
            "pid": os.getpid(),
            "message": kwparams["message"]
        }
        
        time.sleep(5)
        return

    def mark_progress_start(self):
        self._current_progress = TaskingProgress(0, 5, 0, TaskingStatus.Running, self._data)
        return

    def perform(self):

        position = self._current_progress.position

        time.sleep(1)

        morework = False
        if position < self._current_progress.range_max:
            morework = True
            self._current_progress.position = position + 1

        return morework

    def notify_progress(self, progress: TaskingProgress):
        
        position = progress.position
        data = progress.data

        message = data["message"]
        pid = data["pid"]

        print(f"{message} #{position} from {pid}")
        return


def tasking_server_example_main():

    logging_directory = tempfile.mkdtemp(prefix="taskings-")

    controller = ProcessTaskerController(logging_directory=logging_directory)
    controller.start_task_network()

    print("=============== Tasker Nodes ===============")
    for node in controller.tasker_nodes:
        print(f"    ipaddr={node.ipaddr} port={node.port} ...")

    promise_list = controller.execute_task_on_all_nodes(tasking=PrintTasking, message="Hello World")

    for promise in promise_list:
        promise.wait()

    return


if __name__ == "__main__":

    tasking_server_example_main()

