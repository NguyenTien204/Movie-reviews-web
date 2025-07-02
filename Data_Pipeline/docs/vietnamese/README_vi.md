# 🎬 Pipeline Dữ Liệu Phim (Kỹ Thuật Dữ Liệu)

Module này chứa **pipeline kỹ thuật dữ liệu** cốt lõi cho ứng dụng web đề xuất và đánh giá phim. Hệ thống được thiết kế để thu thập, làm sạch, biến đổi và lưu trữ cả metadata phim (từ TMDB API) và log hành vi người dùng (từ frontend) theo thời gian thực hoặc theo lô.

---

## 📦 Tổng Quan Các Thành Phần

### 1. **Kafka** (Thu Thập Dữ Liệu Streaming)
- Chủ đề `user_logs`: nhận tương tác người dùng (xem, đánh giá, bình luận, v.v.)
- Chủ đề `movie`: backup hoặc dữ liệu phim bất đồng bộ từ TMDB API
- `async_producer.py`: đẩy log người dùng từ frontend
- `spark_stream_consumer.py`: tiêu thụ log theo thời gian thực qua Spark Streaming

### 2. **Thu Thập TMDB**
- `tmdb_fetcher.py`: lấy dữ liệu phim từ TMDB API
- `backup_to_kafka.py`: lưu dữ liệu phim vào Kafka để dự phòng
- `MongoDB`: lưu trữ tài liệu JSON thô về phim, backup log thô người dùng từ frontend

### 3. **Spark Jobs**
- `clean_transform.py`: xử lý và chuẩn hóa dữ liệu phim và người dùng
- `enrich_data.py`: làm giàu log người dùng với metadata trước khi chèn vào PostgreSQL

### 4. **PostgreSQL**
Lưu trữ dữ liệu có cấu trúc và quan hệ gồm:
- Phim, thể loại, người dùng
- Đánh giá, bình luận, lượt thích/không thích
- Lịch sử xem, danh sách xem sau
- Hãng sản xuất, ngôn ngữ, quốc gia
- Phiên người dùng và log hành vi (bảng fact)

### 5. **Điều Phối**
- `airflow_dag.py`: điều phối các job theo lô như đồng bộ TMDB hàng ngày, nén log, v.v.

---

## 🛠 Công Nghệ Sử Dụng

| Công Cụ        | Mục Đích                                  |
|----------------|-------------------------------------------|
| **Apache Kafka**     | Streaming log & thu thập dữ liệu thời gian thực |
| **Apache Spark**     | ETL, pipeline biến đổi dữ liệu            |
| **MongoDB**          | Metadata phim TMDB dạng JSON thô         |
| **PostgreSQL**       | Kho dữ liệu có cấu trúc                   |
| **Python (Pandas)**  | Xử lý dữ liệu theo lô & tiện ích         |
| **Apache Airflow**   | Lập lịch và điều phối pipeline            |
| **Flask API**        | Nhận sự kiện người dùng từ frontend       |

---
### 📁 Cấu Trúc Dự Án (Đơn Giản)

```text
movie_data_pipeline/
│
├── kafka/
│   ├── producer/             # Gửi log lên Kafka
│   └── consumer/             # Job Spark Streaming
│
├── ingestion/          # Thu thập & backup TMDB API
├── processing/              # Làm sạch, biến đổi dữ liệu
├── database/                # Schema SQL & loader dữ liệu
├── models/                  # Mô hình đề xuất (tùy chọn)
├── pipelines/               # DAG hoặc job theo lô (Airflow)
├── config/                  # Kết nối & cấu hình xác thực
├── monitoring/              # Tiện ích logging
├── tests/                   # Unit test cho các module dữ liệu
│
├── .env                     # Biến môi trường (API key, DB URI)
├── requirements.txt         # Thư viện Python cần thiết
└── README.md                # File này
```

---

## 🧠 Điểm Nổi Bật Về Schema (PostgreSQL)

Hệ thống sử dụng cấu trúc dạng star schema với bảng dimension và fact. Một số điểm nổi bật:

- `fact_user_event`: theo dõi sự kiện tương tác người dùng
- `dim_session`: phiên người dùng với metadata thiết bị/trình duyệt
- `comments`, `comment_votes`: thảo luận dạng luồng
- `ratings`, `watch_history`, `watchlist`: theo dõi hành vi cốt lõi

---

## 🚀 Bắt Đầu

1. Cài đặt thư viện:  
    - pip install -r requirements.txt

2. Thiết lập biến môi trường:  
    - TMDB_API_KEY=...  
    - POSTGRES_URI=...  

3. Chạy các script thu thập hoặc producer/consumer Kafka theo nhu cầu.

## 📌 Lưu Ý

MongoDB lưu dữ liệu không phù hợp với SQL (ví dụ: JSON thô, log thô,..).  
Thiết kế để mở rộng cho cả pipeline batch và streaming.  

## 📫 Người Phụ Trách

Trưởng nhóm Kỹ Thuật Dữ Liệu: Nguyễn Văn Tiến  
Liên hệ: vantiennguyen1424@gmail.com
