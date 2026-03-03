from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

import pandas as pd


class StorageEngine(ABC):
    @abstractmethod
    def save_price(self, df: pd.DataFrame) -> None: ...

    @abstractmethod
    def save_institutional(self, df: pd.DataFrame) -> None: ...

    @abstractmethod
    def save_per(self, df: pd.DataFrame) -> None: ...

    @abstractmethod
    def get_last_date(self, table: str, data_id: str) -> str | None: ...


class SupportsIncremental(Protocol):
    def get_last_date(self, table: str, data_id: str) -> str | None: ...

