📈 Taiwan Stock Crawler Pro (Cloud Native Edition)

This project implements a cloud‑native, extensible Taiwan stock historical data crawler based on the FinMind API.

Key features:
- Batch & incremental crawling of Taiwan stock historical data
- Parallel downloading with `ThreadPoolExecutor`
- Pluggable storage backends: CSV, SQLite (recommended), DuckDB (future-ready)
- Scheduler mode & CLI one-shot mode
- Docker & docker-compose ready
- Health check endpoint for cloud deployment

See the source files under `app/` for implementation details.

