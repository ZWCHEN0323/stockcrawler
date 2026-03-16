from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List
import httpx
import datetime as dt
from app.utils.logger import logger
from app.utils.retry import with_backoff

BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart"

def _to_timestamp(date_str: str) -> int:
    dt_obj = dt.datetime.strptime(date_str, "%Y-%m-%d")
    return int(dt_obj.timestamp())

@dataclass
class YahooRequest:
    symbol: str
    start_date: str
    end_date: str | None = None
    interval: str = "1d"

    def to_params(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "interval": self.interval,
            "events": "div,splits",
            "period1": _to_timestamp(self.start_date),
        }
        if self.end_date:
            params["period2"] = _to_timestamp(self.end_date)
        return params

class YahooFinanceClient:

    def __init__(self, timeout: float = 10.0) -> None:
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

    @with_backoff(max_tries=1)
    def fetch(self, req: YahooRequest) -> List[Dict[str, Any]]:
        url = f"{BASE_URL}/{req.symbol}"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/112.0.0.0 Safari/537.36"
            )
        }
        logger.info("Fetching Yahoo symbol=%s start=%s end=%s", req.symbol, req.start_date, req.end_date)
        response = self._client.get(url, params=req.to_params(), headers=headers)
        response.raise_for_status()
        data = response.json()
        if not data.get("chart") or not data["chart"].get("result"):
            logger.warning("Yahoo response empty for %s", req.symbol)
            return []
        result = data["chart"]["result"][0]
        timestamps = result["timestamp"]
        quote = result["indicators"]["quote"][0]
        adjclose = result["indicators"].get("adjclose", [{}])[0].get("adjclose", [])
        records: List[Dict[str, Any]] = []
        for i, ts in enumerate(timestamps):
            date = dt.datetime.utcfromtimestamp(ts).date()
            records.append({
                "date": date.isoformat(),
                "open": quote["open"][i],
                "high": quote["high"][i],
                "low": quote["low"][i],
                "close": quote["close"][i],
                "adjusted_close": adjclose[i] if adjclose else None,
                "volume": quote["volume"][i],
            })
        return records

    def close(self) -> None:
        self._client.close()