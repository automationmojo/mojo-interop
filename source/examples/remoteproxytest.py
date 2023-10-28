
import sys

import multiprocessing
import multiprocessing.managers


class TestTasking:

    def method_a(self):
        print ("method-a")
        return
    
    def method_b(self):
        print ("method-b")
        return

def create_tasking(type_name):

    this_module = sys.modules[__name__]

    ctype = getattr(this_module, type_name)

    return ctype()

class TaskerServerManager(multiprocessing.managers.SyncManager):
    """
        This is a process manager used for creating a :class:`TaskerServerManager`
        in a remote process that can be communicated with via a proxy.
    """

TaskerServerManager.register("create_tasking", create_tasking)


if __name__ == "__main__":

    ctx = multiprocessing.get_context("spawn")

    server = TaskerServerManager(ctx=ctx)
    server.start()

    tasking = server.create_tasking("TestTasking")

    tasking.method_a()
    tasking.method_b()

