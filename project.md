# Taiwan Stock Data Crawler

## Project Goal

建立一個可擴展的台股資料抓取系統：

```
FinMind API
    ↓
Crawler
    ↓
Data Cleaning
    ↓
Storage
```

目前主要抓取：

* 股票價格
* 法人買賣
* 本益比

---

# System Architecture

```
app
│
├─ clients
│   └─ finmind_client.py
│
├─ crawler
│   └─ taiwan_stock_crawler.py
│
├─ services
│   └─ stock_service.py
│
├─ storage
│   ├─ base.py
│   ├─ csv_storage.py
│   └─ sqlite_storage.py
│
├─ utils
│   ├─ logger.py
│   └─ retry.py
│
└─ config.py
```

---

# Data Flow

```
StockService
      │
      ▼
TaiwanStockCrawler
      │
      ▼
FinMindClient
      │
      ▼
FinMind API
      │
      ▼
Pandas DataFrame
      │
      ├─ validation
      ├─ normalization
      └─ deduplication
      │
      ▼
StorageEngine
```

---

# Crawled Datasets

| key           | dataset                                  | description |
| ------------- | ---------------------------------------- | ----------- |
| price         | TaiwanStockPrice                         | 股票價格        |
| institutional | TaiwanStockInstitutionalInvestorsBuySell | 法人買賣        |
| per           | TaiwanStockPER                           | 本益比         |

---

# Incremental Crawling

Crawler 會先查詢 storage：

```
get_last_date()
```

然後只抓：

```
last_date → today
```

避免重複抓資料。

---

# Parallel Crawling

系統有兩層 parallel：

## Dataset Parallel

同時抓：

```
price
institutional
per
```

使用：

```
ThreadPoolExecutor(max_workers=3)
```

---

## Stock Parallel

同時抓多個股票：

```
ThreadPoolExecutor(max_workers=settings.max_workers)
```

---

# Storage Abstraction

Storage 使用抽象層：

```
StorageEngine
```

定義：

```
save_price()
save_institutional()
save_per()
get_last_date()
```

目前支援：

```
CsvStorage
SQLiteStorage
```

Crawler 不依賴具體 storage。

---

# Data Processing

Crawler 會做資料清理：

### Validation

過濾：

```
close = 0
Trading_Volume < 0
```

---

### Deduplication

移除重複：

```
(data_id, date)
```

---

### Schema Normalization

API：

```
data_id
```

Storage：

```
stock_id
```

Crawler 會轉換：

```
data_id → stock_id
```

---

# PER 欄位統一

FinMind PER 欄位可能為：

```
PEratio
PER
pe_ratio
peRatio
```

Crawler 會統一為：

```
pe
```

---

# Current Status

✅ FinMind API Client
✅ Retry + Logging
✅ Parallel Crawler
✅ Incremental Crawling
✅ Data Cleaning
✅ Storage Abstraction
⬜ Data Analysis Layer
⬜ Visualization Layer
⬜ Backtesting
