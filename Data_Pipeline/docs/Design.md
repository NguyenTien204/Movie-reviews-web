# 🎬 Movie Review Web Application - Data Pipeline Design Document

---

## ✨ Overview

This document outlines the end-to-end design of the data pipeline supporting the movie review web application. It covers data ingestion, staging, modeling, and serving, with clear responsibilities, tools, and flow for each layer. It is written to ensure that any team member can understand, contribute, or troubleshoot the system effectively.

---

## 🔍 Purpose

The goal of this pipeline is to:

- Collect and process movie metadata, user interactions, and comments.
- Ensure data is stored in both raw and processed forms.
- Support both batch and streaming use cases.
- Enable fast querying and visualizations.

---

## ⚙️ Architecture Overview

```mermaid
flowchart TD
  A[TMDB API & Frontend Logs] --> B[Airflow Scheduler]
  B --> C[MongoDB: Raw Data Layer]
  B --> D[Kafka: Streaming Logs]
  D --> E[Spark Streaming Processor]
  E --> F[PostgreSQL: Analytical DB]
  F --> G[Serving Layer: Metabase / FastAPI]
  E --> H[Monitoring & Logging]
  B --> I[Pandas Batch Processor (Fallback)]
```

## 🚀 Ingestion Layer
### Responsibilities:

- Daily ingest movie data from TMDB API using Airflow.

- Ingest real-time user logs from the frontend into Kafka.

- Backup all logs to MongoDB for redundancy.

### Tools:

- Airflow

- Python (requests, schedule)

- Kafka

- MongoDB

### Design Notes:

- Airflow DAGs scheduled daily or hourly.

- Kafka topics:

    - movie
  
    - user_watch_log
 
    - user_click_log

    - user_comment_log

## 🗂 Staging Layer
### Responsibilities:

- Store raw and semi-structured data.

- Maintain data availability even if other parts fail.

- Tools:

    - MongoDB (raw backups)

    - PostgreSQL (staging tables)

##Structure:

- MongoDB:
  
    - raw.movies
  
    - raw.user_logs
  
- PostgreSQL:

    - stg_movies

    - stg_user_logs

    - stg_comments

## 💡 Modeling Layer
### Responsibilities:

- Clean, enrich, and transform data.

- Support batch and real-time pipelines.

### Streaming (Primary):

- Spark Streaming reads Kafka topics and processes in real-time.

- Outputs to:

  - fact_user_event

  - dim_session

- Batch (Fallback):

    - Pandas is used when Spark is offline.

    - Writes to:

        - fact_user_event_fallback

### Consistency Design:

- All modeling tables include a source_flag column.

- Business logic centralized in transform_rules.json for reuse across tools.

## 🏠 Serving Layer
### Responsibilities:

- Make data queryable for analysis and frontend APIs.

### Tools:

- Metabase (internal dashboards)

- FastAPI (external/public API endpoints)

### Planned API Endpoints:

- /api/top_movies

- /api/user_stats

- /api/emotion_trends

### ⚠️ Fallback & Error Handling
- If Spark fails, fallback to Pandas (controlled by Airflow variable).

- Fallback data is stored separately, not auto-merged.

- Admin manually merges or promotes fallback data if needed.

### 🔧 Future Improvements
- Introduce dbt for unified modeling and testing.

- Replace Pandas fallback with Spark batch jobs.

- Use Great Expectations for data quality validation.

- Build data audit and lineage layer using Airflow metadata.

### 📅 Team Responsibilities
| Role              | Responsibilities                             |
| ----------------- | -------------------------------------------- |
| Data Engineer     | Maintain Airflow, Kafka, Spark jobs          |
| FullStack Developer | Build UI & monitor FastAPI endpoints            |
| ML Engineer           | Use Metabase for data exploration and machine learning            |
| All Members       | Follow schema & transformation specification |

## 🌟 Glossary
- Fact Table: Stores measurable, transactional data (e.g., watch duration).

- Dimension Table: Stores descriptive attributes (e.g., movie genre).

- Source Flag: A column used to track data origin (spark, pandas, etc).

**Version:** 1.0

**Last Updated:** 2025-06-25