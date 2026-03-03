from __future__ import annotations

import argparse
from typing import List, Optional


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Taiwan Stock Crawler Pro CLI",
    )
    parser.add_argument(
        "--stock",
        type=str,
        help="Single stock id (e.g. 2330). If omitted, use STOCK_LIST from env.",
    )
    parser.add_argument(
        "--stocks",
        type=str,
        help="Comma separated stock ids (e.g. 2330,2317,2454).",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        dest="start_date",
        help="Start date YYYY-MM-DD. Default from env START_DATE.",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        dest="end_date",
        help="End date YYYY-MM-DD (optional).",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        choices=[
            "TaiwanStockPrice",
            "TaiwanStockInstitutionalInvestorsBuySell",
            "TaiwanStockPER",
            "all",
        ],
        default="all",
        help="Dataset to crawl (currently always crawls all, kept for compatibility).",
    )
    return parser


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = build_parser()
    return parser.parse_args(argv)

