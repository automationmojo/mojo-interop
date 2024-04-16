
import os
import time

from datetime import datetime

from mojo.results.model.progressinfo import ProgressInfo, ProgressType, ProgressCode

from mojo.interop.protocols.tasker.tasking import Tasking

class HelloWorldTasking(Tasking):

    PREFIX = "helloworld"

    def begin(self, kwparams: dict):

        self._message = kwparams["message"]
        self._iterations = kwparams["iterations"]

        self._data = {
            "pid": os.getpid(),
            "message": self._message,
            "iterations": self._iterations
        }
        
        time.sleep(5)

        return

    def mark_progress_start(self):
        now = datetime.now()
        self._current_progress = ProgressInfo(self._tasking_id, "hello", self.full_name, ProgressType.NumericRange,
                                              0, self._iterations, 0, ProgressCode.Running, now, self._data)
        return

    def log_message(self, message) -> bool:
        self._logger.info(message)
        return True

    def perform(self):

        position = self._current_progress.position

        time.sleep(1)

        morework = False
        if position < self._current_progress.range_max:
            morework = True
            self._current_progress.position = position + 1

        return morework
