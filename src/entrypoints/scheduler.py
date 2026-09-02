import time
from collections.abc import Callable


class Scheduler:
    def __init__(self, interval_seconds: int):
        self._interval_seconds = interval_seconds

    def run_forever(self, task: Callable[[], None]) -> None:
        while True:
            task()
            time.sleep(self._interval_seconds)

    def run_once(self, task: Callable[[], None]) -> None:
        task()
