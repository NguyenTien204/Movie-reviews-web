# 🎬 Movie Data Pipeline (Data Engineering)

This module contains the core **data engineering pipeline** for a movie recommendation and review web application. The system is designed to ingest, clean, transform, and store both movie metadata (from TMDB API) and user-generated behavior logs (from the frontend) in real time or batch mode.

---

## 📦 Components Overview

### 1. **Kafka** (Streaming Ingestion)
- `user_logs` topic: receives user interactions (watch, rate, comment, etc.)
- `movie` topic: backup or async movie data from TMDB API
- `async_producer.py`: pushes user logs from the frontend
- `spark_stream_consumer.py`: consumes logs in real-time via Spark Streaming

### 2. **TMDB Ingestion**
- `fetch_tmdb_data.py`: pulls movie data from the TMDB API
- `backup_to_kafka.py`: stores movie data in Kafka for redundancy
- `MongoDB`: stores raw JSON movie documents, posters, and long comments

### 3. **Spark Jobs**
- `clean_transform.py`: processes and normalizes movie and user data
- `enrich_data.py`: enriches user logs with metadata before insertion into PostgreSQL

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
| **Flask API**        | Receives user events from frontend    |

---
### 📁 Project Structure (Simplified)

```text
movie_data_pipeline/
│
├── kafka/
│   ├── producer/             # Sends logs to Kafka
│   └── consumer/             # Spark Streaming job
│
├── tmdb_ingestion/          # TMDB API ingestion & backup
├── spark_jobs/              # Data cleaning, transformation
├── database/                # SQL schema & data loaders
├── models/                  # Recommendation model (optional)
├── pipelines/               # DAGs or batch jobs (e.g., Airflow)
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

MongoDB stores data not suited for SQL (e.g., raw JSONs, long text, posters).  
Designed to scale both for batch and streaming pipelines.  

## 📫 Maintainer

Data Engineering Lead: Nguyễn Văn Tiến  
Contact: vantiennguyen1424@gmail.com  