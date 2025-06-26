# 📊 Thiết Kế Cơ Sở Dữ Liệu Ứng Dụng Đánh Giá Phim

---

## 1. Tổng Quan

Cơ sở dữ liệu được thiết kế tối ưu cho ứng dụng đánh giá, đề xuất phim, hỗ trợ cả phân tích hành vi người dùng và lưu trữ metadata phim. Hệ thống sử dụng PostgreSQL với mô hình star schema, kết hợp các bảng dimension (mô tả) và fact (giao dịch), đảm bảo hiệu năng truy vấn, mở rộng và tích hợp pipeline dữ liệu batch/streaming.

---

## 2. Mô Hình Dữ Liệu Tổng Thể

- **Người dùng**: Đăng ký, đăng nhập, theo dõi, đánh giá, bình luận phim.
- **Phim**: Metadata chi tiết, thể loại, hãng sản xuất, quốc gia, ngôn ngữ, trailer, bộ sưu tập.
- **Tương tác**: Lịch sử xem, đánh giá, bình luận, bình chọn bình luận, watchlist, sự kiện hành vi.
- **Hỗ trợ phân tích**: Lưu trữ log sự kiện (fact_user_event), phiên người dùng (dim_session).

---

## 3. Các Bảng Chính & Giải Thích

### 3.1. Người Dùng & Quan Hệ

- **users**: Thông tin tài khoản, bảo mật, thời gian tạo/cập nhật.
- **follows**: Quan hệ theo dõi giữa các người dùng (social graph).
- **dim_session**: Lưu thông tin phiên đăng nhập, thiết bị, trình duyệt.

### 3.2. Phim & Metadata

- **movies**: Thông tin phim cơ bản (tên, mô tả, ngôn ngữ, poster, v.v.).
- **genres** & **movie_genres**: Thể loại phim và liên kết nhiều-nhiều.
- **production_companies**, **movie_production_companies**: Hãng sản xuất và liên kết với phim.
- **production_countries**, **movie_production_countries**: Quốc gia sản xuất.
- **spoken_languages**, **movie_spoken_languages**: Ngôn ngữ phim.
- **release_calendar**: Lịch phát hành theo quốc gia, loại phát hành.
- **trailers**: Thông tin trailer, teaser, clip của phim.
- **collections**, **movie_collection**: Bộ sưu tập phim (franchise, series).

### 3.3. Tương Tác Người Dùng

- **watch_history**: Lịch sử xem phim của từng người dùng.
- **ratings**: Đánh giá (score) của người dùng cho phim.
- **comments**: Bình luận của người dùng về phim (dạng luồng).
- **comment_votes**: Bình chọn (like/dislike) cho bình luận.
- **watchlist**: Danh sách phim muốn xem, trạng thái (đang xem, đã xem, dự định, bỏ dở).

### 3.4. Sự Kiện & Phân Tích

- **fact_user_event**: Lưu log sự kiện hành vi (click, view, like, share, comment, watch), metadata mở rộng.
- **dim_session**: Thông tin phiên, liên kết với sự kiện.

---

## 4. Enum & Reference Table

- **watchlist_status_enum**: Trạng thái phim trong watchlist (`watching`, `completed`, `planned`, `dropped`).
- **trailer_type_enum**: Loại trailer (`Trailer`, `Teaser`, `Clip`, `Featurette`).
- **site_enum**: Nguồn video trailer (`YouTube`, `Vimeo`).
- **event_type_enum**: Loại sự kiện hành vi (`click`, `view`, `like`, `share`, `comment`, `watch`).

---

## 5. Quan Hệ & Ràng Buộc

- **Khóa ngoại**: Đảm bảo toàn vẹn dữ liệu giữa các bảng (user, movie, session, v.v.).
- **Bảng liên kết nhiều-nhiều**: movie_genres, movie_production_companies, movie_production_countries, movie_spoken_languages, movie_collection.
- **Ràng buộc duy nhất**: username, email (users); (user_id, movie_id) (watchlist); (user_id, comment_id) (comment_votes).
- **CHECK**: Không cho phép người dùng tự theo dõi chính mình (follows).

---

## 6. Chỉ Mục (Indexes)

- **idx_ratings_movie_id**: Tăng tốc truy vấn đánh giá theo phim.
- **idx_watch_history_user_id**: Tăng tốc truy vấn lịch sử xem theo người dùng.
- **idx_fact_user_event_type**: Tăng tốc phân tích sự kiện theo loại.
- **idx_comments_movie_id**: Tăng tốc truy vấn bình luận theo phim.
- **idx_trailers_movie_id**: Tăng tốc truy vấn trailer theo phim.

---

## 7. Lưu Ý Thiết Kế & Mở Rộng

- **UUID**: Sử dụng cho id bình luận, sự kiện để đảm bảo phân tán và tích hợp streaming.
- **JSONB**: Trường metadata trong fact_user_event cho phép lưu dữ liệu mở rộng, linh hoạt.
- **Soft Delete**: Trường `is_deleted` cho phép ẩn dữ liệu thay vì xóa vật lý.
- **Star Schema**: Phù hợp cho phân tích, BI, truy vấn tổng hợp.
- **Batch & Streaming**: Thiết kế hỗ trợ cả pipeline batch (Pandas) và streaming (Spark).
- **Mở rộng**: Dễ dàng thêm các dimension mới (ví dụ: đạo diễn, diễn viên), hoặc fact table mới cho hành vi khác.

---

## 8. Sơ Đồ Quan Hệ (ERD) - Mô Tả Văn Bản

- **users** (1) --- (N) **watch_history**, **ratings**, **comments**, **watchlist**, **fact_user_event**, **dim_session**
- **movies** (1) --- (N) **watch_history**, **ratings**, **comments**, **watchlist**, **fact_user_event**, **trailers**, **release_calendar**
- **movies** (N) --- (N) **genres**, **production_companies**, **production_countries**, **spoken_languages**, **collections** (thông qua bảng liên kết)
- **comments** (1) --- (N) **comment_votes**
- **users** (N) --- (N) **follows** (theo dõi lẫn nhau)
- **dim_session** (1) --- (N) **fact_user_event**

---

## 9. Ví Dụ Truy Vấn Thường Gặp

- Lấy top phim theo điểm đánh giá trung bình.
- Truy vấn lịch sử xem của một người dùng.
- Thống kê số lượt xem, bình luận, đánh giá theo phim.
- Phân tích hành vi người dùng theo loại sự kiện (event_type).
- Lọc phim theo thể loại, quốc gia, hãng sản xuất.

---

## 10. Tham Khảo & Liên Hệ

- **Schema chi tiết**: Xem file `database/schema.sql`
- **Mô tả pipeline**: Xem `README.md`, `Design.md`
- **Liên hệ kỹ thuật**: Nguyễn Văn Tiến (vantiennguyen1424@gmail.com)

---
