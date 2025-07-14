## 🎯 **1. Auth Router (`/auth`)**
Quản lý xác thực và người dùng cơ bản.
- `POST /auth/register`: Đăng ký tài khoản mới
    
- `POST /auth/login`: Đăng nhập
    
- `POST /auth/logout`: Đăng xuất
    
- `POST /auth/token-refresh`: Làm mới token nếu dùng JWT

## 👤 **2. User Router (`/users`)**
Thông tin và hoạt động của người dùng.

- `GET /users/me`: Lấy thông tin người dùng hiện tại
    
- `GET /users/me/logs`: hoạt động người dùng (user log)
    
- `PATCH /users/me`: Cập nhật thông tin hồ sơ

- `GET /reviews/user/{user_id}`: Đánh giá của người dùng

## 🎬 **3. Movie Router (`/movies`)**

Thông tin phim từ TMDB hoặc cơ sở dữ liệu nội bộ.

- `GET /movies/{movie_id}`: Chi tiết một phim

- `GET /shortdetail/{movie_id}`: Chi tiết ngắn hiển thị trang home

- `GET /movies/filter:` lọc phim
    
- `GET /movies/trending`: Phim đang thịnh hành
    
- `GET /movies/{movie_id}/trailer`: Trailer phim
    
- `GET /movies/{movie_id}/recommendations`: Gợi ý phim tương tự
 

## ⭐ **4. Rating Router (`/ratings`)**

Chấm điểm phim.

- `POST /ratings/`: Người dùng chấm điểm một phim
    
- `PUT /ratings/{rating_id}`: Cập nhật điểm đã chấm
    
- `GET /ratings/{movie_id}`: Lấy điểm trung bình và phân phối điểm phim

## 📝 **5. Review Router (`/reviews`)**

Viết đánh giá ngắn về phim.

- `POST /reviews/`: Viết đánh giá
    
- `PUT /reviews/{review_id}`: Chỉnh sửa đánh giá
    
- `DELETE /reviews/{review_id}`: Xóa đánh giá
    
- `GET /reviews/{movie_id}`: Danh sách đánh giá của một phim
    
## ⚡ **6. Search Router (`/search`)**

Tìm kiếm toàn cục cho blog, phim, người dùng...

- `GET /search/instant`: Gợi ý khi gõ từ khóa
    
- `GET /search/full`: Tìm kiếm nâng cao có lọc theo loại nội dung, phân loại 