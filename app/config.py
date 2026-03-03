import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv


load_dotenv()


def _get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


@dataclass
class Settings:
    finmind_api_token: str
    stock_list: List[str]
    data_path: str
    db_type: str
    run_mode: str
    log_level: str
    max_workers: int
    start_date: str


def get_settings() -> Settings:
    token = _get_env("FINMIND_API_TOKEN", "")
    stock_list_raw = _get_env("STOCK_LIST", "")
    stock_list = [s.strip() for s in stock_list_raw.split(",") if s.strip()]

    return Settings(
        finmind_api_token=token,
        stock_list=stock_list,
        data_path=_get_env("DATA_PATH", "./data"),
        db_type=_get_env("DB_TYPE", "sqlite"),
        run_mode=_get_env("RUN_MODE", "once"),
        log_level=_get_env("LOG_LEVEL", "INFO"),
        max_workers=int(_get_env("MAX_WORKERS", "5")),
        start_date=_get_env("START_DATE", "2026-01-01"),
    )


settings = get_settings()

