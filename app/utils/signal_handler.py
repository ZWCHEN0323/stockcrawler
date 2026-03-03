import signal
from typing import Callable

from app.utils.logger import logger


class GracefulKiller:
    def __init__(self, stop_callback: Callable[[], None]) -> None:
        self.stop_callback = stop_callback
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum: int, frame) -> None:  # type: ignore[override]
        logger.info("Received signal %s, shutting down gracefully...", signum)
        self.stop_callback()

