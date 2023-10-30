
import os
import tempfile
import time
import threading


from mojo.interop.protocols.tasker.taskeraspects import TaskerAspects
from mojo.interop.protocols.tasker.taskercontroller import ProcessTaskerController

from mojo.results.model.progressinfo import ProgressInfo, ProgressType, ProgressCode

from mojo.interop.protocols.tasker.tasking import Tasking
from mojo.interop.protocols.tasker.taskingresult import TaskingResult

from http.server import HTTPServer, BaseHTTPRequestHandler

class NotifyRequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):

        content_length = self.headers['content-length']
        length = int(content_length) if content_length else 0

        print("------------- Processing Notification-------------")
        print(self.rfile.read(length).decode())
        print("--------------------------------------------------")
        print("")

        self.send_response(200, message=None)
        self.send_header("Content-Type", "application/type")
        self.end_headers()

        return



class PrintTasking(Tasking):

    def begin(self, kwparams: dict):

        self._data = {
            "pid": os.getpid(),
            "message": kwparams["message"]
        }
        
        time.sleep(5)

        return

    def mark_progress_start(self):
        self._current_progress = ProgressInfo(self._task_id, ProgressType.NumericRange, self.full_name, ProgressType.NumericRange,
                                              0, 5, 0, ProgressCode.Running, self._data)
        return

    def perform(self):

        position = self._current_progress.position

        time.sleep(1)

        morework = False
        if position < self._current_progress.range_max:
            morework = True
            self._current_progress.position = position + 1

        return morework


def notify_server_main(sgate: threading.Event, notify_addr: str, notify_port: int):

    notify_server = HTTPServer((notify_addr, notify_port), NotifyRequestHandler)

    sgate.set()

    notify_server.serve_forever()
    return

def tasking_server_example_main():

    notify_addr = ""
    notify_port = 8686

    nsgate = threading.Event()
    nsgate.clear()

    notifyth = threading.Thread(target=notify_server_main, name="notify-svr", args=(nsgate, notify_addr, notify_port), daemon=True)
    notifyth.start()

    # Wait for the notify server to spin up before continuing
    nsgate.wait()

    logging_directory = tempfile.mkdtemp(prefix="taskerrun-")

    controller = ProcessTaskerController(logging_directory=logging_directory)
    controller.start_tasker_network(notify_url=f'http://localhost:{notify_port}/')

    print("=============== Tasker Nodes ===============")
    for node in controller.tasker_nodes:
        print(f"    ipaddr={node.ipaddr} port={node.port} ...")

    promise_list = controller.execute_task_on_all_nodes(tasking=PrintTasking, message="Hello World")

    for promise in promise_list:
        promise.wait()

    for promise in promise_list:
        result: TaskingResult = promise.get_result()
        print(f"RESULT - {promise.task_name}")
        print(f"    id: {promise.task_id}")
        print(f"    parent: {result.parent_id}")
        print(f"    start: {result.start}")
        print(f"   logdir: {result.logdir}")
        print(f"    stop: {result.stop}")
        print(f"    result_code: {result.result_code}")
        print(f"    exception: {result.exception}")
        print("")


    return


if __name__ == "__main__":

    tasking_server_example_main()

