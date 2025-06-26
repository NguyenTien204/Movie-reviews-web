# 🎬 Ứng Dụng Đánh Giá Phim - Tài Liệu Thiết Kế Pipeline Dữ Liệu

---

## ✨ Tổng Quan

Tài liệu này mô tả thiết kế end-to-end của pipeline dữ liệu hỗ trợ ứng dụng web đánh giá phim. Bao gồm các lớp thu thập, staging, mô hình hóa và phục vụ dữ liệu, với trách nhiệm, công cụ và luồng xử lý rõ ràng cho từng lớp. Viết nhằm đảm bảo mọi thành viên đều có thể hiểu, đóng góp hoặc xử lý sự cố hệ thống hiệu quả.

---

## 🔍 Mục Đích

Mục tiêu của pipeline này là:

- Thu thập và xử lý metadata phim, tương tác người dùng, và bình luận.
- Đảm bảo dữ liệu được lưu trữ cả dạng thô và đã xử lý.
- Hỗ trợ cả xử lý theo lô và thời gian thực.
- Cho phép truy vấn và trực quan hóa nhanh chóng.

---

## ⚙️ Tổng Quan Kiến Trúc

```mermaid
flowchart TD
  A[TMDB API & Frontend Logs] --> B[Airflow Scheduler]
  B --> C[MongoDB: Lớp Dữ Liệu Thô]
  B --> D[Kafka: Streaming Logs]
  D --> E[Spark Streaming Processor]
  E --> F[PostgreSQL: DB Phân Tích]
  F --> G[Lớp Phục Vụ: Metabase / FastAPI]
  E --> H[Giám Sát & Logging]
  B --> I[Xử Lý Batch Pandas (Dự Phòng)]
```

## 🚀 Lớp Thu Thập Dữ Liệu (Ingestion)
### Trách Nhiệm:

- Thu thập dữ liệu phim từ TMDB API hàng ngày bằng Airflow.
- Nhận log người dùng thời gian thực từ frontend vào Kafka.
- Backup toàn bộ log vào MongoDB để dự phòng.

### Công Cụ:

- Airflow
- Python (requests, schedule)
- Kafka
- MongoDB

### Ghi Chú Thiết Kế:

- Airflow DAG lên lịch hàng ngày hoặc hàng giờ.
- Các topic Kafka:
    - movie
    - user_watch_log
    - user_click_log
    - user_comment_log

## 🗂 Lớp Staging

### Trách Nhiệm:

- Lưu trữ dữ liệu thô và bán cấu trúc.
- Đảm bảo dữ liệu luôn sẵn sàng kể cả khi các phần khác gặp sự cố.

### Công Cụ:

- MongoDB (backup thô)
- PostgreSQL (bảng staging)

### Cấu Trúc:

- MongoDB:
    - raw.movies
    - raw.user_logs
- PostgreSQL:
    - stg_movies
    - stg_user_logs
    - stg_comments

## 💡 Lớp Mô Hình Hóa (Modeling)

### Trách Nhiệm:

- Làm sạch, làm giàu và biến đổi dữ liệu.
- Hỗ trợ cả pipeline batch và streaming.

### Streaming (Chính):

- Spark Streaming đọc các topic Kafka và xử lý thời gian thực.
- Ghi ra:
  - fact_user_event
  - dim_session

### Batch (Dự Phòng):

- Dùng Pandas khi Spark offline.
- Ghi ra:
    - fact_user_event_fallback

### Thiết Kế Tính Nhất Quán:

- Tất cả bảng modeling đều có cột source_flag.
- Logic nghiệp vụ tập trung trong transform_rules.json để tái sử dụng giữa các công cụ.

## 🏠 Lớp Phục Vụ (Serving Layer)

### Trách Nhiệm:

- Cho phép truy vấn dữ liệu phục vụ phân tích và API frontend.

### Công Cụ:

- Metabase (dashboard nội bộ)
- FastAPI (API endpoint công khai)

### Các API Dự Kiến:

- /api/top_movies
- /api/user_stats
- /api/emotion_trends

### ⚠️ Dự Phòng & Xử Lý Lỗi

- Nếu Spark lỗi, chuyển sang Pandas (điều khiển qua biến Airflow).
- Dữ liệu dự phòng lưu riêng, không tự động gộp.
- Admin sẽ merge hoặc promote dữ liệu fallback khi cần.

### 🔧 Cải Tiến Tương Lai

- Thêm dbt để thống nhất modeling và kiểm thử.
- Thay Pandas fallback bằng Spark batch job.
- Sử dụng Great Expectations để kiểm tra chất lượng dữ liệu.
- Xây dựng lớp kiểm toán và lineage dữ liệu bằng metadata Airflow.

### 📅 Trách Nhiệm Nhóm

| Vai Trò              | Trách Nhiệm                                      |
| -------------------- | ----------------------------------------------- |
| Kỹ Sư Dữ Liệu        | Duy trì Airflow, Kafka, Spark jobs              |
| Lập Trình Viên FullStack | Xây dựng UI & giám sát endpoint FastAPI           |
| Kỹ Sư ML             | Khai thác Metabase cho phân tích và học máy     |
| Tất Cả Thành Viên    | Tuân thủ schema & quy tắc biến đổi dữ liệu      |

## 🌟 Thuật Ngữ

- Bảng Fact: Lưu trữ dữ liệu giao dịch, đo lường (ví dụ: thời lượng xem).
- Bảng Dimension: Lưu trữ thuộc tính mô tả (ví dụ: thể loại phim).
- Source Flag: Cột dùng để theo dõi nguồn gốc dữ liệu (spark, pandas, v.v.).

**Phiên bản:** 1.0

**Cập nhật lần cuối:** 2025-06-25
