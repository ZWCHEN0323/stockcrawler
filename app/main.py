from __future__ import annotations

import sys
from typing import List

from app.cli import parse_args
from app.config import settings
from app.health.health_server import start_health_server
from app.scheduler.scheduler import Scheduler
from app.services.stock_service import StockService
from app.utils.logger import logger
from app.utils.signal_handler import GracefulKiller


def run_once(argv: List[str]) -> None:
    args = parse_args(argv)
    service = StockService.create()

    stocks: List[str]
    if args.stocks:
        stocks = [s.strip() for s in args.stocks.split(",") if s.strip()]
    elif args.stock:
        stocks = [args.stock]
    else:
        stocks = settings.stock_list

    start_date = args.start_date or settings.start_date
    end_date = args.end_date

    logger.info(
        "Running once with stocks=%s start_date=%s end_date=%s",
        stocks,
        start_date,
        end_date,
    )
    service.crawl(stocks, start_date=start_date, end_date=end_date)


def run_schedule() -> None:
    service_factory = StockService.create
    scheduler = Scheduler(service_factory=service_factory)

    killer = GracefulKiller(stop_callback=scheduler.stop)
    _ = killer

    # optional health server
    start_health_server()

    scheduler.start_daily_job(at="18:00")


def main() -> None:
    logger.info("Starting Taiwan Stock Crawler Pro, mode=%s", settings.run_mode)
    if settings.run_mode == "once":
        run_once(sys.argv[1:])
    else:
        run_schedule()


if __name__ == "__main__":
    main()

