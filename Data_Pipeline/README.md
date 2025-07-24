# 🎬 Movie Data Pipeline (Data Engineering)

This module contains the core **data engineering pipeline** for a movie recommendation and review web application. The system is designed to ingest, clean, transform, and store both movie metadata (from TMDB API) and user-generated behavior logs (from the frontend) in real time or batch mode.

---

## 📦 Components Overview

### 1. **Kafka** (Streaming Ingestion)
- `Topic`: click, rating, trailer, search, dwelltime 
- `clean_transform.py`: consumes logs in real-time via Spark Streaming

### 2. **TMDB Ingestion**
- `tmdb_fetcher.py`: pulls movie data from the TMDB API
- `MongoDB`: stores raw JSON movie documents, backup raw user log from frontend

### 3. **Spark Jobs**
- `clean_transform.py`: processes user log data
- `enrich_data.py`: enriches user logs with metadata from history and PostgreSQL

### 4. **PostgreSQL**
Stores the structured and relational version of:
- Movies, genres, users
- Ratings, comments, likes/dislikes
- Watch history, watchlists
- Production companies, languages, countries
- User sessions and behavioral logs (fact tables)

### 5. **Orchestration**
- `airflow_dag.py`: orchestrates batch jobs such as daily TMDB sync, log compaction, etc.

---

## 🛠 Tech Stack

| Tool        | Purpose                                  |
|-------------|------------------------------------------|
| **Apache Kafka**     | Real-time streaming of logs & ingestion |
| **Apache Spark**     | ETL jobs, transformation pipelines    |
| **MongoDB**          | Raw TMDB movie metadata (JSON)       |
| **PostgreSQL**       | Structured data warehouse             |
| **Python (Pandas)**  | Batch data processing & utilities     |
| **Apache Airflow**   | Scheduling and orchestration          |
| **FAST API**        | Receives user events from frontend    |

---
### 📁 Data Structure (Simplified)

```text
movie_data_pipeline/
│
├── kafka_consumer/          # Kafka consumer 
│
├── ingestion/               # TMDB API ingestion & backup
├── processing/              # Data cleaning, processing transformation
├── database/                # SQL schema & data loaders
├── pipelines/               # DAGs or batch jobs 
├── config/                  # Connection & auth configs
├── monitoring/              # Logging utilities
├── tests/                   # Unit tests for data modules
│
├── .env                     # Environment variables (API keys, DB URI)
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## 🧠 Schema Highlights (PostgreSQL)

The system uses a star schema-like structure with dimension and fact tables. Example highlights:

- `fact_user_event`: tracks user interaction events
- `dim_session`: user sessions with device/browser metadata
- `comments`, `comment_votes`: threaded user discussions
- `ratings`, `watch_history`, `watchlist`: core behavior tracking

---

## 🚀 Getting Started

1. Install dependencies:  
    - pip install -r requirements.txt

2. Set environment variables:  
    - TMDB_API_KEY=...  
    - POSTGRES_URI=...  

3. Run ingestion scripts or Kafka producers/consumers as needed.

## 📌 Notes

MongoDB stores data not suited for SQL (e.g., raw JSONs, raw log,..).  
Designed to scale both for batch and streaming pipelines.  

## 📚 Detailed documents:
### **English version**
> **[Database Design](./docs/Database.md)**  
> **[Pipeline Design](./docs/Design.md)**
### **Vietnamese version**
> **[README](./docs/vietnamese/README_vi.md)**  
> **[Database Design](./docs/vietnamese/Database_vi.md)**  
> **[Pipeline Design](./docs/vietnamese/Design_vi.md)**

## 📫 Maintainer

Data Engineering Lead: Nguyễn Văn Tiến  
Contact: vantiennguyen1424@gmail.com  