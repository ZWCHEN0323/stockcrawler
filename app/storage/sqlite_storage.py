from __future__ import annotations

import os
import sqlite3
import threading
from typing import Iterable

import pandas as pd

from app.config import settings
from app.storage.base import StorageEngine
from app.utils.logger import logger


DB_PATH = os.path.join(settings.data_path, "stock.db")


class SQLiteStorage(StorageEngine):
    def __init__(self) -> None:
        os.makedirs(settings.data_path, exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self._lock = threading.Lock()
        self._init_tables()

    def _init_tables(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS stock_price (
                stock_id TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                max REAL,
                min REAL,
                close REAL,
                Trading_Volume REAL,
                PRIMARY KEY (stock_id, date)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS stock_institutional (
                stock_id TEXT NOT NULL,
                date TEXT NOT NULL,
                buy REAL,
                sell REAL,
                PRIMARY KEY (stock_id, date)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS stock_per (
                stock_id TEXT NOT NULL,
                date TEXT NOT NULL,
                pe REAL,
                PRIMARY KEY (stock_id, date)
            )
            """
        )
        self.conn.commit()

    def _upsert(self, table: str, df: pd.DataFrame, columns: Iterable[str]) -> None:
        if df.empty:
            return
        cols = ",".join(columns)
        placeholders = ",".join(["?"] * len(columns))
        sql = f"INSERT OR REPLACE INTO {table} ({cols}) VALUES ({placeholders})"
        logger.debug("Upserting %d rows into %s", len(df), table)
        with self._lock:
            cur = self.conn.cursor()
            cur.executemany(sql, df[list(columns)].itertuples(index=False, name=None))
            self.conn.commit()

    def save_price(self, df: pd.DataFrame) -> None:
        self._upsert(
            "stock_price",
            df,
            [
                "stock_id",
                "date",
                "open",
                "max",
                "min",
                "close",
                "Trading_Volume",
            ],
        )

    def save_institutional(self, df: pd.DataFrame) -> None:
        self._upsert("stock_institutional", df, ["stock_id", "date", "buy", "sell"])

    def save_per(self, df: pd.DataFrame) -> None:
        self._upsert("stock_per", df, ["stock_id", "date", "pe"])

    def get_last_date(self, table: str, data_id: str) -> str | None:
        table_map = {
            "price": "stock_price",
            "institutional": "stock_institutional",
            "per": "stock_per",
        }
        tname = table_map.get(table, table)
        with self._lock:
            cur = self.conn.cursor()
            cur.execute(
                f"SELECT MAX(date) FROM {tname} WHERE stock_id = ?", (data_id,)
            )
            row = cur.fetchone()
        return row[0] if row and row[0] is not None else None

