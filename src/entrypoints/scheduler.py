import logging
import signal
import threading
from collections.abc import Callable

logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(self, interval_seconds: int):
        self._interval_seconds = interval_seconds
        self._stop_event = threading.Event()
        self._setup_signals()

    def _setup_signals(self) -> None:
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum: int, frame: object) -> None:
        logger.info("Shutting down after current task...")
        self._stop_event.set()

    def run_forever(self, task: Callable[[], None]) -> None:
        while not self._stop_event.is_set():
            task()
            if not self._stop_event.is_set():
                self._stop_event.wait(self._interval_seconds)

    def run_once(self, task: Callable[[], None]) -> None:
        task()
