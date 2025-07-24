# 🎬 Movie Insight Platform
**Dự án Web Đánh Giá Phim** kết hợp hệ thống phân tích, dự đoán và hiển thị thông tin phim thời gian thực, hỗ trợ người dùng tìm kiếm, xem trailer, viết đánh giá, và nhận gợi ý phim cá nhân hóa dựa trên hành vi.

## 📁 Mục lục
Giới thiệu

[Kiến trúc tổng quan]()

[1. Machine Learning]()

[2. Data Pipeline]()

[3. Web Frontend & Backend]()

[Cài đặt và Chạy thử]()

[Công nghệ sử dụng]()

[Đóng góp]()

[Giấy phép]()

## 🎯 Giới thiệu
Đây là một dự án khoa học dữ liệu ứng dụng trong lĩnh vực giải trí. Nền tảng kết hợp giữa:

- Hệ thống web hỗ trợ đánh giá, theo dõi phim.

- Mô hình ML gợi ý phim theo hành vi người dùng.

- Hệ thống xử lý dữ liệu theo kiến trúc streaming + batch hiện đại.


## 🧱 Kiến trúc tổng quan

![Structure Diagram](/docs/Diagram/Untitled%20Diagram.drawio.png)

## 1. 🔍 Machine Learning
`📌 Mục tiêu: Dự đoán sở thích người dùng và gợi ý phim dựa trên hành vi.`

### 📦 Các thành phần chính:
- Tập dữ liệu huấn luyện: user_log, ratings, movie metadata từ web và database
 
- Tiền xử lý:

    - ☐ Encoding thể loại phim

    - ☐ Kết hợp dữ liệu hành vi (click, rating, search, trailer, dwelltime) 

- Mô hình sử dụng:
- Gợi ý cá nhân hóa:
  - ☐ Top-N gợi ý theo từng người dùng

  - ☐ Gợi ý phim trending
 
> 🧠 TODO: Điền chi tiết về pipeline huấn luyện, metric đánh giá và quá trình triển khai mô hình.

## 2. 🔄 Data Pipeline
`📌 Mục tiêu: Thu thập – xử lý – đồng bộ dữ liệu từ frontend đến backend, phục vụ cả real-time và batch.`

### 🎯 Thành phần chính:
#### 🔹 Kafka:
- Phân chia topic theo hành vi: click, search, rating, dwelltime, trailer

- Frontend gửi log trực tiếp lên Kafka producer

#### 🔹 Spark Streaming:
- Consume log theo topic

- Làm giàu với metadata phim (từ MongoDB và PostgreSQL)

- Đẩy dữ liệu đã xử lý vào PostgreSQL

#### 🔹 MongoDB:
- Lưu raw movie data từ TMDB API

- Dự phòng dữ liệu log dạng JSON 

#### 🔹PostgreSQL:
- Lưu dữ liệu phim đã làm sạch
- Database OLTP cho hạ tầng web

#### 🔹 Airflow:
- Orchestrate pipeline batch mỗi ngày:

- Crawl dữ liệu TMDB (movie, genre, trailer,…)

- Đồng bộ từ Mongo → PostgreSQL

- Huấn luyện lại mô hình 

> 🧠 TODO: Thêm sơ đồ DAG Airflow nếu có, thông số Spark submit, chiến lược fallback khi Kafka/Spark lỗi.

## 3. 🖥 Web Frontend & Backend 
### 🌐 Frontend (HTML/JS/CSS)
**📌 Tính năng:**

- Giao diện tối giản, responsive

- Xem thông tin phim, trailer

> 🧠 TODO: Nhúng GIF giao diện demo, liệt kê các component chính 

### ⚙️ Backend (FastAPI)
**📌 Tính năng:**
- Quản lý người dùng: đăng ký, đăng nhập

- API lấy danh sách phim, chi tiết, filter/sort

- API viết đánh giá, like/dislike, rating

- Log hành vi gửi Kafka

- Tích hợp mô hình ML để trả về gợi ý theo user

#### **Cấu trúc backend chia theo service (class-based):**
```
App/
├── backend/            
│   ├── api/            # Routes
│   ├── services/       # Logic nghiệp vụ
│   ├── models/         # Database ORM
│   ├── core/           # Bảo mật
│   └── schema/         # Xác thực dữ liệu từ db
```

## 🛠 Cài đặt và Chạy thử
### Yêu cầu
```
Python >= 3.10
NodeJS >= 18.x
MongoDB, PostgreSQL, Kafka, Spark, Airflow
```

### Chạy backend
```
cd App/backend
pip install -r requirements.txt
uvicorn main:app --reload
```
### Chạy frontend
```
```

## ⚙ TechStack
| Layer         | Công nghệ                         |
| ------------- | --------------------------------- |
| Frontend      | HTML, CSS, JavaScript             |
| Backend API   | FastAPI, Pydantic, SQLAlchemy     |
| Cơ sở dữ liệu | PostgreSQL, MongoDB               |
| Streaming     | Kafka, Spark Structured Streaming |
| Orchestration | Airflow                           |
| ML            | PySpark MLlib / scikit-learn      |
| Visualization | Streamlit / Metabase (tuỳ chọn)   |


## 🤝 Đóng góp
> Mọi đóng góp (ý tưởng, báo lỗi, tính năng mới) đều được hoan nghênh. Hãy tạo pull request hoặc mở issue.

## 📜 Giấy phép
MIT License © 2025 