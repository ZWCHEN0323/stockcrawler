from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable, Dict, Any, List
import pandas as pd
import datetime as dt
import time

from app.api.yahoo_finance_client import YahooFinanceClient, YahooRequest
from app.config import settings
from app.storage.base import StorageEngine
from app.utils.logger import logger

def _validate_row(row: Dict[str, Any]) -> bool:
    if float(row.get("close", 0)) <= 0:
        return False
    if float(row.get("volume", 0)) < 0:
        return False
    return True

def to_yahoo_symbol(stock_id: str) -> str:
    return f"{stock_id}.TW"

def _split_periods(start_date: str, end_date: str, years_per_batch: int = 3) -> List[tuple[str, str]]:
    """
    將抓取日期拆成多個 batch，每 batch 年份數 = years_per_batch
    """
    start = dt.datetime.strptime(start_date, "%Y-%m-%d")
    end = dt.datetime.strptime(end_date, "%Y-%m-%d")
    periods = []
    while start < end:
        batch_end = min(start.replace(year=start.year + years_per_batch), end)
        periods.append((start.strftime("%Y-%m-%d"), batch_end.strftime("%Y-%m-%d")))
        start = batch_end + dt.timedelta(days=1)
    return periods

class TaiwanStockCrawler:

    def __init__(self, client: YahooFinanceClient, storage: StorageEngine) -> None:
        self.client = client
        self.storage = storage

    def _fetch_price_batch(self, stock_id: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        抓取單個股票、單個 batch（幾年）的歷史資料
        """
        symbol = to_yahoo_symbol(stock_id)
        req = YahooRequest(symbol=symbol, start_date=start_date, end_date=end_date)
        data = self.client.fetch(req)
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        df["stock_id"] = stock_id
        df = df[df.apply(_validate_row, axis=1)]
        df = df.drop_duplicates(subset=["stock_id", "date"])
        return df

    def _fetch_price(self, stock_id: str, start_date: str) -> pd.DataFrame:
        """
        根據 storage 最後日期增量抓
        拆批抓歷史，避免 429
        """
        last_date = self.storage.get_last_date("price", stock_id)
        effective_start = last_date or start_date
        today = dt.datetime.today().strftime("%Y-%m-%d")
        periods = _split_periods(effective_start, today, years_per_batch=3)
        all_batches = []
        for batch_start, batch_end in periods:
            df = self._fetch_price_batch(stock_id, batch_start, batch_end)
            if not df.empty:
                all_batches.append(df)
            time.sleep(1.5)  # 避免 429
        if all_batches:
            return pd.concat(all_batches, ignore_index=True)
        return pd.DataFrame()

    def crawl_stock(self, stock_id: str, start_date: str | None = None) -> None:
        start = start_date or settings.start_date
        logger.info("Start crawling stock %s from %s", stock_id, start)
        try:
            df = self._fetch_price(stock_id, start)
            if df.empty:
                logger.info("No new data for %s", stock_id)
                return
            self.storage.save_price(df)
            logger.info("Saved %d rows for %s price", len(df), stock_id)
        except Exception as exc:
            logger.exception("Failed to crawl %s: %s", stock_id, exc)

    def crawl_many(self, stocks: Iterable[str], start_date: str | None = None) -> None:
        start = start_date or settings.start_date
        stocks = list(stocks)
        logger.info("Start batch crawling %d stocks", len(stocks))
        with ThreadPoolExecutor(max_workers=settings.max_workers) as executor:
            future_to_stock = {executor.submit(self.crawl_stock, stock, start): stock for stock in stocks}
            for fut in as_completed(future_to_stock):
                stock = future_to_stock[fut]
                try:
                    fut.result()
                except Exception as exc:
                    logger.exception("Failed to crawl stock %s: %s", stock, exc)