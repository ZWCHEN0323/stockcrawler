# PROJECT STATUS — Taiwan Stock Data Platform

## 1️⃣ Current Completion

| Layer / Feature     | Status      | Notes                                                                                  |
| ------------------- | ----------- | -------------------------------------------------------------------------------------- |
| CLI Entry           | ✅ Completed | `main.py`, `cli.py`                                                                    |
| Scheduler           | ✅ Completed | Daily job at 18:00, supports graceful shutdown                                         |
| StockService        | ✅ Completed | Service layer orchestrates crawler and storage                                         |
| TaiwanStockCrawler  | ✅ Completed | Parallel dataset & stock crawling, incremental update, data validation & normalization |
| FinMindClient       | ✅ Completed | HTTP client with retry, timeout, auth token, fetch API                                 |
| Storage Abstraction | ✅ Completed | `StorageEngine` interface with `CsvStorage` and `SQLiteStorage`                        |
| Logging             | ✅ Completed | Standardized logging across service and crawler                                        |
| Retry / Backoff     | ✅ Completed | Decorator applied to API calls                                                         |
| Docker              | ✅ Completed | Dockerfile + docker-compose ready                                                      |
| Health Server       | ✅ Completed | Optional HTTP endpoint for service health                                              |

---

## 2️⃣ Missing / Not Yet Implemented

| Feature                    | Status            | Notes                                                         |
| -------------------------- | ----------------- | ------------------------------------------------------------- |
| Data Analysis Layer        | ⬜ Not implemented | Analysis or computation over stored data                      |
| Visualization / Plotting   | ⬜ Not implemented | Charts, graphs, dashboards                                    |
| Backtesting / Strategy     | ⬜ Not implemented | Future module for investment strategy testing                 |
| Rate Limiting              | ⬜ Not implemented | To avoid hitting FinMind API limits                           |
| Async Crawling             | ⬜ Not implemented | Currently uses ThreadPoolExecutor; could be upgraded          |
| Cache Layer                | ⬜ Not implemented | Redis / DuckDB optional for faster incremental updates        |
| Data Warehouse Integration | ⬜ Not implemented | For long-term storage and analytics (PostgreSQL / ClickHouse) |

---

## 3️⃣ Next Steps / Recommendations

1. **Short-term**

   * Implement visualization module using `plot` folder
   * Add optional CLI flags for custom stock lists or datasets
   * Consider handling missing PER / other dataset anomalies

2. **Medium-term**

   * Add async API requests with `httpx.AsyncClient`
   * Introduce rate limiter or queue to respect API limits
   * Add caching layer for already fetched data

3. **Long-term / Strategic**

   * Integrate with a Data Warehouse (PostgreSQL / ClickHouse)
   * Build analysis & backtesting modules
   * Refactor crawler to be fully event-driven / scalable

---

## 4️⃣ Current Strengths

* Production-level crawler architecture
* Incremental & parallel crawling
* Data validation & schema normalization
* Storage abstraction allows easy swap of CSV / SQLite
* Logging and retry mechanisms built-in
* Fully Dockerized and ready for deployment

---

## 5️⃣ Overall Status

```text
Progress: 70–75% complete
Core functionality ✅
Analysis / Visualization / Strategy ⬜
```

This file gives an **at-a-glance view** of what is done, what is missing, and where to go next.
