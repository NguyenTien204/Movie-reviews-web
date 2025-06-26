# 🎬 Ứng Dụng Đánh Giá Phim - Tài Liệu Thiết Kế Pipeline Dữ Liệu

---

## ✨ Tổng Quan

Tài liệu này mô tả chi tiết thiết kế end-to-end của pipeline dữ liệu cho ứng dụng web đánh giá phim. Bao gồm luồng dữ liệu, thu thập, staging, mô hình hóa, phục vụ và phân tích, với trách nhiệm, lựa chọn công nghệ và lý do rõ ràng cho từng lớp. Mục tiêu là đảm bảo mọi thành viên đều có thể hiểu, đóng góp hoặc xử lý sự cố hệ thống hiệu quả.

---

## 🔄 Luồng Dữ Liệu: Từ Nguồn Đến Phục Vụ

**1. Nguồn Dữ Liệu:**
- **TMDB API**: Cung cấp metadata phim (tên, thể loại, hãng sản xuất, v.v.).
- **Frontend (Web/App)**: Gửi log tương tác người dùng (xem, đánh giá, bình luận, click, v.v.).

**2. Thu Thập (Ingestion):**
- **Airflow** lên lịch và điều phối các job batch để lấy dữ liệu phim từ TMDB API.
- **Frontend** đẩy log người dùng thời gian thực vào các topic **Kafka**.

**3. Staging:**
- **MongoDB** lưu trữ dữ liệu JSON thô từ TMDB và log người dùng để backup và truy cập bán cấu trúc.
- **Kafka** đóng vai trò buffer và backbone streaming cho sự kiện người dùng thời gian thực.

**4. Xử Lý & Mô Hình Hóa:**
- **Spark Streaming** tiêu thụ các topic Kafka, làm sạch, biến đổi và làm giàu dữ liệu gần như real-time.
- **Pandas** batch job (dự phòng) xử lý dữ liệu nếu Spark không khả dụng.

**5. Lưu Trữ:**
- **PostgreSQL** lưu dữ liệu có cấu trúc, quan hệ và phục vụ phân tích (star schema: bảng fact & dimension).

**6. Phục Vụ (Serving):**
- **Metabase** cho dashboard nội bộ và phân tích.
- **FastAPI** cho RESTful API phục vụ frontend và client ngoài.
- (Tùy chọn) **Streamlit** hoặc công cụ khác cho khám phá dữ liệu nhanh.

**7. Mô Hình ML:**
- Huấn luyện trên dữ liệu từ PostgreSQL (đánh giá, lịch sử xem, sự kiện người dùng).
- Trả về đề xuất hoặc phân tích, phục vụ qua API hoặc dashboard.

---

## ❓ Vì Sao Chọn Các Công Nghệ Này?

### Vì sao chọn Kafka? Vì sao không chỉ dùng MongoDB?

- **Kafka** được thiết kế cho streaming throughput cao, tách biệt producer (frontend) và consumer (job xử lý). Kafka đảm bảo độ bền, mở rộng, khả năng replay sự kiện.
- **MongoDB** phù hợp lưu dữ liệu thô, bán cấu trúc, nhưng không hỗ trợ streaming, ordering, consumer group như Kafka.
- **Kafka** cho phép phân tích real-time, xử lý sự kiện, ingestion chịu lỗi mà MongoDB không đáp ứng được.

### Spark xử lý gì? Real-time hay just-in-time batch?

- **Spark Streaming** xử lý sự kiện người dùng và dữ liệu phim gần như real-time, phục vụ phân tích, đề xuất, dashboard cập nhật liên tục.
- Real-time cần thiết cho thống kê trực tiếp, phim trending, đề xuất tức thời.
- **Batch (Pandas)** dùng dự phòng cho reliability hoặc xử lý offline nặng (job ban đêm, backfill).

### Tại sao backup vào MongoDB?

- **MongoDB** là backup cho toàn bộ dữ liệu thô (metadata phim, log người dùng), đảm bảo không mất dữ liệu nếu downstream lỗi.
- Hỗ trợ reprocessing, debug, và các use case cần dữ liệu thô (data science, kiểm thử).

### Tại sao dùng PostgreSQL để truy vấn?

- **PostgreSQL** đảm bảo nhất quán, mô hình quan hệ, indexing, và khả năng phân tích SQL mạnh.
- Tối ưu cho truy vấn phức tạp, tổng hợp, tích hợp BI/ML pipeline.
- Thiết kế star schema giúp truy vấn phân tích nhanh, dễ tích hợp dashboard.

---

## ⚙️ Tổng Quan Kiến Trúc

```mermaid
flowchart TD
  A[TMDB API & Frontend Logs] --> B[Airflow Scheduler]
  B --> C[MongoDB: Lớp Dữ Liệu Thô]
  B --> D[Kafka: Streaming Logs]
  D --> E[Spark Streaming Processor]
  E --> F[PostgreSQL: DB Phân Tích]
  F --> G[Lớp Phục Vụ: Metabase / FastAPI / Streamlit]
  E --> H[Giám Sát & Logging]
  B --> I[Xử Lý Batch Pandas (Dự Phòng)]
```

---

## 🚀 Lớp Thu Thập Dữ Liệu (Ingestion)

### Trách Nhiệm

- **Airflow**: Lên lịch job lấy dữ liệu phim từ TMDB API, điều phối ETL batch.
- **Frontend**: Gửi sự kiện người dùng (xem, đánh giá, bình luận,...) vào Kafka real-time.
- **Backup**: Tất cả dữ liệu thu thập đều lưu vào MongoDB để dự phòng và truy cập thô.

### Công Cụ

- Airflow, Python (requests, schedule), Kafka, MongoDB

### Ghi Chú Thiết Kế

- Các topic Kafka: `movie`, `user_watch_log`, `user_click_log`, `user_comment_log`
- Airflow DAG quản lý cả batch và fallback.

---

## 🗂 Lớp Staging

### Trách Nhiệm

- Lưu dữ liệu thô, bán cấu trúc để đảm bảo reliability và reprocessing.
- Đảm bảo dữ liệu luôn sẵn sàng kể cả khi downstream lỗi.

### Công Cụ

- MongoDB (backup thô)
- PostgreSQL (bảng staging cho ETL)

### Cấu Trúc

- MongoDB: `raw.movies`, `raw.user_logs`
- PostgreSQL: `stg_movies`, `stg_user_logs`, `stg_comments`

---

## 💡 Lớp Mô Hình Hóa & Xử Lý

### Trách Nhiệm

- Làm sạch, làm giàu, biến đổi dữ liệu phục vụ phân tích và ML.
- Hỗ trợ cả pipeline streaming (real-time) và batch (dự phòng).

### Streaming (Chính)

- **Spark Streaming** đọc từ Kafka, xử lý sự kiện, ghi vào bảng fact/dimension PostgreSQL.
- Đáp ứng phân tích, dashboard, đề xuất gần real-time.

### Batch (Dự Phòng)

- **Pandas** xử lý batch từ MongoDB/Kafka nếu Spark lỗi.
- Dùng cho job ban đêm, backfill, hoặc khôi phục.

### Thiết Kế Nhất Quán

- Tất cả bảng modeling có cột `source_flag` để theo dõi nguồn dữ liệu (spark, pandas,...).
- Logic nghiệp vụ tập trung trong `transform_rules.json` để đồng nhất giữa các công cụ.

---

## 🏠 Lớp Phục Vụ (Serving Layer)

### Trách Nhiệm

- Cung cấp dữ liệu đã xử lý cho phân tích, dashboard, API.

### Công Cụ

- **Metabase**: Dashboard nội bộ cho business/technical.
- **FastAPI**: RESTful API cho frontend và client ngoài.
- **Streamlit** (tùy chọn): Khám phá dữ liệu nhanh, prototyping.

### Các API Dự Kiến

- `/api/top_movies`
- `/api/user_stats`
- `/api/emotion_trends`
- `/api/recommendations` (từ mô hình ML)

---

## 🤖 Tích Hợp Mô Hình ML

- **Nguồn dữ liệu**: ML train trên dữ liệu từ PostgreSQL (đánh giá, lịch sử xem, sự kiện,...).
- **Phục vụ**: Kết quả (đề xuất, phân tích) trả về qua endpoint FastAPI hoặc dashboard Metabase/Streamlit.
- **Người dùng cuối**: Frontend, dashboard, hoặc dịch vụ khác có thể lấy đề xuất/analytics.

---

## ⚠️ Dự Phòng & Xử Lý Lỗi

- Nếu Spark lỗi, Airflow chuyển sang Pandas batch (qua biến Airflow).
- Dữ liệu fallback lưu riêng, không tự động merge; admin chủ động promote nếu cần.
- Dữ liệu thô luôn backup ở MongoDB để khôi phục, reprocessing.

---

## 🔧 Cải Tiến Tương Lai

- Thêm **dbt** để thống nhất modeling, kiểm thử.
- Thay Pandas fallback bằng Spark batch cho đồng nhất.
- Sử dụng **Great Expectations** kiểm tra chất lượng dữ liệu.
- Xây dựng audit, lineage bằng metadata Airflow.
- Tích hợp mô hình ML nâng cao, phục vụ real-time.

---

## 📅 Trách Nhiệm Nhóm

| Vai Trò                | Trách Nhiệm                                      |
|------------------------|--------------------------------------------------|
| Kỹ Sư Dữ Liệu          | Duy trì Airflow, Kafka, Spark, chất lượng dữ liệu|
| Lập Trình Viên FullStack | Xây dựng UI & giám sát endpoint FastAPI         |
| Kỹ Sư ML               | Khai thác Metabase/SQL cho phân tích & ML        |
| Tất Cả Thành Viên      | Tuân thủ schema & quy tắc biến đổi dữ liệu       |

---

## 🌟 Thuật Ngữ

- **Bảng Fact**: Lưu dữ liệu giao dịch, đo lường (vd: thời lượng xem).
- **Bảng Dimension**: Lưu thuộc tính mô tả (vd: thể loại phim).
- **Source Flag**: Cột theo dõi nguồn dữ liệu (spark, pandas,...).
- **Serving Layer**: API/dashboard cung cấp dữ liệu đã xử lý cho người dùng.

---

**Phiên bản:** 1.1  
**Cập nhật lần cuối:** 2025-06-27
