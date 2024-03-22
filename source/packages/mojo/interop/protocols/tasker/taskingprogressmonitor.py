
from typing import List, TYPE_CHECKING

import threading
import time
import weakref

from mojo.results.model.progressdelivery import SummaryProgressDelivery
from mojo.results.model.progresscode import ProgressCode


if TYPE_CHECKING:
    from mojo.interop.protocols.tasker.taskingresultpromise import TaskingResultPromise
    

class TaskingProgressMonitor:

    def __init__(self, summary_progress: SummaryProgressDelivery, monitored_promises: List["TaskingResultPromise"]):

        self._progress_callback = summary_progress.progress_callback
        self._progress_interval = summary_progress.progress_interval

        self._lock = threading.Lock()
        self._monitored_promise_refs = { pr.tasking_id: weakref.ref(pr) for pr in monitored_promises }
        self._clear_progress_for = [ pr.tasking_id for pr in monitored_promises]
        return
    
    def release(self, tasking_id: str):

        self._lock.acquire()
        try:
            del self._monitored_promise_refs[tasking_id]
        finally:
            self._lock.release()

        return

    def start(self):

        sgate = threading.Event()
        sgate.clear()

        self._progress_thread = threading.Thread(target=self._pull_progress_entry, name="progress-pullback", args=(sgate,), daemon=True)
        self._progress_thread.start()

        sgate.wait()

        return

    def _pull_progress_entry(self, sgate: threading.Event):

        self._pulling_progress = True

        sgate.set()

        while self._pulling_progress:

            time.sleep(self._progress_interval)

            promises: List["TaskingResultPromise"] = []
            self._lock.acquire()
            try:
                if len(self._monitored_promise_refs) == 0:
                    break

                for pref in self._monitored_promise_refs.values():
                    p = pref()
                    if p is not None:
                        promises.append(p)
            finally:
                self._lock.release()

            completed_list: List["TaskingResultPromise"] = []
            progress_list = []
            for prom_item in promises:
                try:
                    progress = prom_item.get_progress()
                    
                    if progress.status != ProgressCode.NotStarted and progress.status != ProgressCode.Paused and \
                    progress.status != ProgressCode.Running:
                        completed_list.append(progress)

                    progress_list.append(progress)
                except:
                    completed_list.append(progress)

            self._lock.acquire()
            try:
                for prog in completed_list:
                    tasking_id = prog.tasking_id
                    del self._monitored_promise_refs[tasking_id]
            finally:
                self._lock.release()
            
            self._progress_callback(progress_list)

        return
