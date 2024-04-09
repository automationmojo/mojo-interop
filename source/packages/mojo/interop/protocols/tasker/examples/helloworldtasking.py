
import os
import time

from datetime import datetime

from mojo.results.model.progressinfo import ProgressInfo, ProgressType, ProgressCode

from mojo.interop.protocols.tasker.tasking import Tasking

class HelloWorldTasking(Tasking):

    PREFIX = "helloworld"

    def begin(self, kwparams: dict):

        self._data = {
            "pid": os.getpid(),
            "message": kwparams["message"]
        }
        
        time.sleep(5)

        return

    def mark_progress_start(self):
        now = datetime.now()
        self._current_progress = ProgressInfo(self._tasking_id, "hello", self.full_name, ProgressType.NumericRange,
                                              0, 5, 0, ProgressCode.Running, now, self._data)
        return

    def perform(self):

        position = self._current_progress.position

        time.sleep(1)

        morework = False
        if position < self._current_progress.range_max:
            morework = True
            self._current_progress.position = position + 1

        return morework
