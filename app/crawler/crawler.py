from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable, Dict, Any, List

import pandas as pd

from app.api.finmind_client import FinMindClient, FinMindRequest
from app.config import settings
from app.storage.base import StorageEngine
from app.utils.logger import logger


DATASETS = {
    "price": "TaiwanStockPrice",
    "institutional": "TaiwanStockInstitutionalInvestorsBuySell",
    "per": "TaiwanStockPER",
}


def _validate_row(row: Dict[str, Any]) -> bool:
    if float(row.get("close", 0)) == 0:
        return False
    if float(row.get("Trading_Volume", 0)) < 0:
        return False
    return True


class TaiwanStockCrawler:
    def __init__(self, client: FinMindClient, storage: StorageEngine) -> None:
        self.client = client
        self.storage = storage

    def _fetch_dataset(
        self, dataset_key: str, data_id: str, start_date: str
    ) -> pd.DataFrame:
        dataset = DATASETS[dataset_key]
        last_date = self.storage.get_last_date(dataset_key, data_id)
        effective_start = last_date or start_date
        req = FinMindRequest(
            dataset=dataset,
            data_id=data_id,
            start_date=effective_start,
        )
        data = self.client.fetch(req)
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        if "data_id" not in df.columns:
            df["data_id"] = data_id
        # 專案規則：API 與一般程式內使用 data_id，DB 欄位使用 stock_id
        # 因此在存進 DB 前，複製一個 stock_id 欄位供 SQLite 使用
        df["stock_id"] = df["data_id"]
        # FinMind TaiwanStockPER 欄位名稱可能不是 pe（例如 PEratio），這裡統一轉成 pe
        if dataset_key == "per":
            if "pe" not in df.columns:
                alt_cols = ["PEratio", "PER", "pe_ratio", "peRatio"]
                for col in alt_cols:
                    if col in df.columns:
                        df = df.rename(columns={col: "pe"})
                        break
        if "date" not in df.columns:
            raise ValueError("FinMind response missing 'date' column")
        if "close" in df.columns or "Trading_Volume" in df.columns:
            df = df[df.apply(_validate_row, axis=1)]
        df = df.drop_duplicates(subset=["data_id", "date"])
        return df

    def crawl_stock(self, data_id: str, start_date: str | None = None) -> None:
        start = start_date or settings.start_date
        logger.info("Start crawling stock %s from %s", data_id, start)
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self._fetch_dataset, key, data_id, start): key
                for key in DATASETS
            }
            for fut in as_completed(futures):
                key = futures[fut]
                try:
                    df = fut.result()
                    if df.empty:
                        logger.info("No new data for %s %s", data_id, key)
                        continue
                    if key == "price":
                        self.storage.save_price(df)
                    elif key == "institutional":
                        self.storage.save_institutional(df)
                    elif key == "per":
                        self.storage.save_per(df)
                    logger.info(
                        "Saved %d rows for %s %s", len(df), data_id, key
                    )
                except Exception as exc:
                    logger.exception(
                        "Failed to crawl %s %s: %s", data_id, key, exc
                    )

    def crawl_many(
        self, stocks: Iterable[str], start_date: str | None = None
    ) -> None:
        start = start_date or settings.start_date
        logger.info("Start batch crawling %d stocks", len(list(stocks)))
        with ThreadPoolExecutor(max_workers=settings.max_workers) as executor:
            future_to_stock = {
                executor.submit(self.crawl_stock, stock, start): stock
                for stock in stocks
            }
            for fut in as_completed(future_to_stock):
                stock = future_to_stock[fut]
                try:
                    fut.result()
                except Exception as exc:
                    logger.exception("Failed to crawl stock %s: %s", stock, exc)

