from __future__ import annotations

import os
from typing import Literal

import pandas as pd

from app.config import settings
from app.storage.base import StorageEngine


DATASET_TO_FILE: dict[str, tuple[str, Literal["price", "institutional", "per"]]] = {
    "TaiwanStockPrice": ("price", "price"),
    "TaiwanStockInstitutionalInvestorsBuySell": ("institutional", "institutional"),
    "TaiwanStockPER": ("per", "per"),
}


class CsvStorage(StorageEngine):
    def __init__(self) -> None:
        os.makedirs(settings.data_path, exist_ok=True)

    def _path(self, data_id: str, kind: str) -> str:
        return os.path.join(settings.data_path, f"{data_id}_{kind}.csv")

    def _append_dedup(self, path: str, df: pd.DataFrame) -> None:
        if os.path.exists(path):
            old = pd.read_csv(path)
            merged = pd.concat([old, df], ignore_index=True)
            merged = merged.drop_duplicates(subset=["data_id", "date"]).sort_values(
                "date"
            )
        else:
            merged = df.sort_values("date")
        merged.to_csv(path, index=False)

    def save_price(self, df: pd.DataFrame) -> None:
        if df.empty:
            return
        data_id = str(df.iloc[0]["data_id"])
        self._append_dedup(self._path(data_id, "price"), df)

    def save_institutional(self, df: pd.DataFrame) -> None:
        if df.empty:
            return
        data_id = str(df.iloc[0]["data_id"])
        self._append_dedup(self._path(data_id, "institutional"), df)

    def save_per(self, df: pd.DataFrame) -> None:
        if df.empty:
            return
        data_id = str(df.iloc[0]["data_id"])
        self._append_dedup(self._path(data_id, "per"), df)

    def get_last_date(self, table: str, data_id: str) -> str | None:
        path = self._path(data_id, table)
        if not os.path.exists(path):
            return None
        df = pd.read_csv(path, usecols=["date"])
        if df.empty:
            return None
        return str(df["date"].max())

