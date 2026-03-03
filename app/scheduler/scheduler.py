from __future__ import annotations

import threading
import time
from typing import Callable

import schedule

from app.services.stock_service import StockService
from app.utils.logger import logger


class Scheduler:
    def __init__(self, service_factory: Callable[[], StockService]) -> None:
        self.service_factory = service_factory
        self._stop_event = threading.Event()

    def start_daily_job(self, at: str = "18:00") -> None:
        logger.info("Scheduling daily crawl at %s", at)

        def job() -> None:
            logger.info("Running scheduled crawl job")
            service = self.service_factory()
            service.crawl_default()

        schedule.every().day.at(at).do(job)

        while not self._stop_event.is_set():
            schedule.run_pending()
            time.sleep(1)

        logger.info("Scheduler loop stopped.")

    def stop(self) -> None:
        logger.info("Stopping scheduler...")
        self._stop_event.set()

