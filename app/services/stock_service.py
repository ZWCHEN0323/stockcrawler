from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from app.api.yahoo_finance_client import YahooFinanceClient
from app.config import settings
from app.crawler.crawler import TaiwanStockCrawler
from app.storage.base import StorageEngine
from app.storage.csv_storage import CsvStorage
from app.storage.sqlite_storage import SQLiteStorage
from app.utils.logger import logger


def build_storage() -> StorageEngine:
    if settings.db_type == "sqlite":
        return SQLiteStorage()
    return CsvStorage()


@dataclass
class StockService:
    crawler: TaiwanStockCrawler

    @classmethod
    def create(cls) -> "StockService":
        client = YahooFinanceClient()
        storage = build_storage()
        crawler = TaiwanStockCrawler(client=client, storage=storage)
        return cls(crawler=crawler)

    def crawl_default(self) -> None:
        logger.info("Crawling default stock list: %s", settings.stock_list)
        self.crawler.crawl_many(settings.stock_list, start_date=settings.start_date)

    def crawl(
        self,
        stock_ids: Iterable[str],
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> None:
        """
        end_date 在 Yahoo API 版本目前可以忽略，
        因為 incremental crawl 已經只抓 last_date → today
        """
        _ = end_date
        self.crawler.crawl_many(stock_ids, start_date=start_date or settings.start_date)