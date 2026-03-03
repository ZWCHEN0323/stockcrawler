from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List

import httpx

from app.config import settings
from app.utils.logger import logger
from app.utils.retry import with_backoff


BASE_URL = "https://api.finmindtrade.com/api/v4/data"


@dataclass
class FinMindRequest:
    dataset: str
    data_id: str
    start_date: str
    end_date: str | None = None

    def to_params(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "dataset": self.dataset,
            "data_id": self.data_id,
            "start_date": self.start_date,
            # "token": settings.finmind_api_token,
        }
        if self.end_date:
            params["end_date"] = self.end_date
        return params


class FinMindClient:
    def __init__(self, timeout: float = 10.0) -> None:
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

    @with_backoff(max_tries=3)
    def fetch(self, req: FinMindRequest) -> List[Dict[str, Any]]:
        logger.info(
            "Fetching dataset=%s stock=%s start=%s end=%s",
            req.dataset,
            req.data_id,
            req.start_date,
            req.end_date,
        )
        headers = {
            "Authorization": f"Bearer {settings.finmind_api_token}"
        }
        response = self._client.get(BASE_URL, params=req.to_params(),headers=headers,)
        response.raise_for_status()
        data = response.json()
        if data.get("status") != 200:
            raise RuntimeError(f"FinMind error: {data}")
        return data.get("data", [])

    def close(self) -> None:
        self._client.close()

