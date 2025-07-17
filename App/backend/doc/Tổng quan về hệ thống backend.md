### 1. **Giới thiệu chung**

Trong quá trình xây dựng các hệ thống web hiện đại, việc tổ chức cấu trúc thư mục một cách khoa học và có định hướng từ đầu là một yếu tố cực kỳ quan trọng nhằm đảm bảo khả năng mở rộng, tái sử dụng, dễ bảo trì và cộng tác nhóm. Dự án này sử dụng **FastAPI** – một framework Python hiện đại, hiệu năng cao – làm nền tảng cho backend. Báo cáo này trình bày chi tiết cấu trúc thư mục backend của dự án, giải thích vai trò và chức năng của từng phần.
### 2. Cấu trúc thư mục
```
backend/
│
├── main.py                          # Điểm khởi chạy FastAPI app
├── requirments.txt                  # Danh sách thư viện cần cài
│
├── api/                             # Các route/endpoint chính của app
│   ├── __init__.py                  # Import các router
│   ├── auth.py                      # Xác thực: login, register
│   ├── movie.py                     # Route phim
│   ├── rating.py                    # Route chấm điểm phim
│   ├── reviews.py                   # Route đánh giá phim
│   ├── search.py                    # Route tìm kiếm
│   └── user.py                      # Route người dùng
│
├── core/                            # Cấu hình và bảo mật
│   └── security.py                  # Xử lý JWT, OAuth2, hash mật khẩu
│
├── db/                              # Cấu hình database
│   ├── __init__.py
│   └── config.py                    # (gợi ý) chứa biến môi trường, DB URL
│
├── models/                          # ORM models (SQLAlchemy)
│   ├── __init__.py
│   ├── base.py                      # Base = declarative_base()
│   ├── enums.py                     # Enum kiểu dữ liệu
│   ├── event.py                     # (tùy chọn) nếu có bảng event
│   ├── movie.py                     # Model phim
│   └── user.py                      # Model người dùng
│
├── schema/                          # Pydantic schemas (input/output)
│   ├── __init__.py
│   ├── movie.py                     # Schema phim
│   ├── review.py                    # Schema đánh giá
│   └── user.py                      # Schema người dùng
│
└── service/                         # Business logic (tách khỏi route)
    └── movie_service.py             # Logic xử lý phim

```
### 3. **Phân tích chi tiết từng thành phần**

#### 3.1. **Thư mục `api/` – Xử lý các tuyến (routes) của ứng dụng**

Thư mục này chứa các endpoint mà frontend hoặc người dùng có thể gọi để tương tác với hệ thống. Mỗi file đại diện cho một module chức năng riêng biệt, ví dụ:

- `auth.py`: Định nghĩa các API phục vụ cho xác thực (đăng nhập, đăng ký).
    
- `movie.py`: Xử lý các thao tác CRUD phim.
    
- `rating.py`, `reviews.py`: Xử lý đánh giá và chấm điểm cho phim.
    
- `search.py`: Hỗ trợ truy vấn tìm kiếm phim.
    
- `user.py`: Các API liên quan đến người dùng.
    

Tổ chức module hóa theo tính năng như trên giúp mã nguồn dễ đọc và mở rộng.

#### 3.2. **Thư mục `core/` – Các cấu hình hệ thống và bảo mật**

Thư mục `core/` thường dùng để chứa các thiết lập cốt lõi:

- `security.py`: Cài đặt logic xác thực bảo mật như mã hóa mật khẩu (bcrypt), xử lý JWT (JSON Web Token), và các hàm hỗ trợ kiểm tra quyền truy cập người dùng.
    

Có thể mở rộng thêm:

- `config.py`: Load các biến môi trường như `SECRET_KEY`, `DATABASE_URL` từ file `.env`.
    

#### 3.3. **Thư mục `db/` – Quản lý cơ sở dữ liệu**

Thư mục này chịu trách nhiệm cấu hình kết nối đến cơ sở dữ liệu.

- `config.py`: Có thể dùng để định nghĩa cấu hình kết nối đến PostgreSQL hoặc SQLite.
    
- `__init__.py`: Đảm bảo thư mục được công nhận là module Python.
    

Đề xuất mở rộng:

- `session.py`: Tạo session SQLAlchemy (`SessionLocal`), cung cấp hàm `get_db()` để sử dụng trong dependency injection của FastAPI.
    

#### 3.4. **Thư mục `models/` – Các mô hình ORM**

Đây là nơi định nghĩa các bảng cơ sở dữ liệu bằng SQLAlchemy.

- `base.py`: Tạo `Base = declarative_base()` – nền tảng để các model kế thừa.
    
- `movie.py`, `user.py`, `event.py`: Mỗi file tương ứng với một bảng dữ liệu như `Movie`, `User`, `Event`.
    
- `enums.py`: Các Enum dùng trong bảng (ví dụ: thể loại phim, quyền hạn người dùng).
    

Việc tách nhỏ giúp dễ bảo trì khi có hàng chục bảng dữ liệu.

#### 3.5. **Thư mục `schema/` – Định nghĩa dữ liệu vào/ra với Pydantic**

FastAPI sử dụng Pydantic để xác thực dữ liệu. Thư mục `schema/` định nghĩa các class để:

- Kiểm tra dữ liệu gửi từ người dùng (input).
    
- Cấu trúc dữ liệu trả về cho client (output).
    

Ví dụ:

- `movie.py`: Gồm các schema như `MovieCreate`, `MovieUpdate`, `MovieResponse`.
    
- `review.py`: Xác định schema đánh giá.
    
- `user.py`: Schema cho đăng ký, login, trả về thông tin người dùng.
    

Tách schema khỏi models là một best-practice để tránh phụ thuộc lẫn nhau giữa logic ORM và logic xác thực.

#### 3.6. **Thư mục `service/` – Chứa logic nghiệp vụ (business logic)**

Thay vì viết hết logic xử lý vào file route (`api/`), ta tách phần xử lý này sang `service/`.

- `movie_service.py`: Chứa các hàm xử lý như tạo phim, lọc phim theo điểm đánh giá, xử lý các rule phức tạp.
    

Điều này giúp route code gọn hơn, dễ test logic độc lập.
### 4. **Các tệp tin chính khác**

- `main.py`: Điểm khởi chạy ứng dụng FastAPI. Bao gồm:
    
    - Tạo đối tượng `FastAPI()`
        
    - Khai báo middleware như CORS
        
    - Import và `include_router()` từ `api/`
        
    - Có thể định nghĩa sự kiện khởi động hoặc shutdown
        
- `requirements.txt`: Ghi lại các thư viện Python cần thiết để chạy dự án. 

### 5. **Kết luận**

Việc thiết kế cấu trúc thư mục một cách có hệ thống giúp đảm bảo mã nguồn rõ ràng, dễ mở rộng, bảo trì lâu dài. Mô hình phân tách theo module và theo chức năng (routes, schema, model, service) như trong dự án này là một hướng tiếp cận hiện đại và phù hợp với các dự án sử dụng FastAPI. Dựa vào cấu trúc trên, nhóm phát triển có thể dễ dàng phân chia công việc, tái sử dụng code, đồng thời đảm bảo độ an toàn và khả năng mở rộng cho hệ thống backend.