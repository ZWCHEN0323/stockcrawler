# Taiwan Stock Data Crawler (Yahoo Finance Version)

## Project Goal

建立一個可擴展的台股資料抓取系統（改為 Yahoo Finance）：  


YahooFinance API
↓
Crawler
↓
Data Cleaning
↓
Storage


目前主要抓取：  

* 調整後股價（adjusted_close）
* 成交量
* 法人買賣（可選，若有資料源）
* 本益比（可選，若有資料源）

---

# System Architecture


app
│
├─ api
│ └─ yahoo_finance_client.py
│
├─ crawler
│ └─ crawler.py
│
├─ services
│ └─ stock_service.py
│
├─ storage
│ ├─ base.py
│ ├─ csv_storage.py
│ └─ sqlite_storage.py
│
├─ utils
│ ├─ logger.py
│ └─ retry.py
│
└─ config.py


---

# Data Flow


StockService
│
▼
TaiwanStockCrawler
│
▼
YahooFinanceClient
│
▼
YahooFinance API
│
▼
Pandas DataFrame
│
├─ validation
├─ normalization
└─ deduplication
│
▼
StorageEngine (Csv / SQLite)


---

# Crawled Datasets

| key   | dataset             | description              |
| ----- | ----------------- | ----------------------- |
| price | TaiwanStockPrice   | 調整後股價 + 成交量       |
| per   | TaiwanStockPER     | 本益比（可選）           |
| institutional | TaiwanStockInstitutionalInvestorsBuySell | 法人買賣（可選） |

> 調整股價存於 `adjusted_close` 欄位，存 CSV / SQLite 時可選覆蓋 `close`。

---

# Incremental Crawling

Crawler 會先查詢 storage：


get_last_date()


然後只抓：


last_date → today


避免重複抓資料。

---

# Batch Crawling (拆批抓歷史)

Yahoo Finance 會限制短時間大量請求 → 易 429  

Crawler 會自動將抓取區間拆成多個 batch，每 batch 預設 3 年：


start_date → batch_end (3年) → 下一 batch → today


每 batch 完成後會 sleep 1~2 秒，減少被封鎖機率。

---

# Parallel Crawling

系統有兩層 parallel：

## Dataset Parallel

目前只抓 price，可以保留擴展欄位。

## Stock Parallel

同時抓多個股票：


ThreadPoolExecutor(max_workers=settings.max_workers)


---

# Storage Abstraction

Storage 使用抽象層：


StorageEngine


定義：


save_price()
save_institutional()
save_per()
get_last_date()


目前支援：


CsvStorage
SQLiteStorage


Crawler 不依賴具體 storage。

> CsvStorage 與 SQLiteStorage 已更新為支援 Yahoo Finance 的 stock_id 與 adjusted_close。

---

# Data Processing

Crawler 會做資料清理：

### Validation

過濾：


close <= 0
volume < 0


### Deduplication

移除重複：


(stock_id, date)


### Schema Normalization

- Yahoo Finance 使用 `stock_id`  
- 調整股價欄位 `adjusted_close`  
- 可選覆蓋 `close` 欄位，方便回測  

---

# Current Status

✅ YahooFinance API Client  
✅ Retry + Logging  
✅ Parallel Crawler  
✅ Incremental Crawling  
✅ Batch Crawling (拆批 + 限速)  
✅ Data Cleaning  
✅ Storage Abstraction  
⬜ Data Analysis Layer  
⬜ Visualization Layer  
⬜ Backtesting