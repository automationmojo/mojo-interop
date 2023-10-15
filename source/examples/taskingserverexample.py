
import os
import tempfile


from mojo.interop.protocols.tasker.taskercontroller import ProcessTaskerController
from mojo.interop.protocols.tasker.tasking import Tasking


class PrintTasking(Tasking):

    def perform(self, *, message, **kwargs):
        
        pid = os.getpid()
        print(f"({pid}) {message}")

        return


def tasking_server_example_main():

    logging_directory = tempfile.mkdtemp(prefix="taskings-")

    controller = ProcessTaskerController(logging_directory=logging_directory)
    controller.start_task_network()

    print("=============== Tasker Nodes ===============")
    for node in controller.tasker_nodes:
        print(f"    ipaddr={node.ipaddr} port={node.port} ...")

    controller.execute_task_on_all_nodes(module_name="__main__", tasking_name="PrintTasking", message="Hello World")

    return


if __name__ == "__main__":

    tasking_server_example_main()

