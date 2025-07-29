
import { getVideoUrl } from '../utils/getUrl.js';
import { getScoreDescription,processGenres} from '../utils/createHome.js';
import { API_CONFIG } from '../api/config.js';

document.addEventListener("DOMContentLoaded", async () => {
    // 1. Lấy movie_id từ URL
    const params = new URLSearchParams(window.location.search);
    const movieId = params.get("movie_id");

    if (!movieId) {
        console.error("Không có movie_id trong URL.");
        return;
    }

    try {
        // 2. Gọi API để lấy dữ liệu chi tiết
        const response = await fetch(`${API_CONFIG.BASE_URL}/movies/${movieId}`);

        if (!response.ok) {
            throw new Error("Không thể lấy dữ liệu phim.");
        }

        const movie = await response.json();
        const videoUrl = await getVideoUrl(movie.movie_id);
        const genreUrl = processGenres(movie.genres).map(genre =>`<span class="movie-genre">${genre}</span>`).join('');
        console.log(videoUrl);
        document.querySelector(".detail-movie-title").textContent = movie.title || "Không có tiêu đề";
        document.querySelector(".summary").textContent = movie.overview || "Không có mô tả";
        document.querySelector(".main-video").src = videoUrl || "Không rõ";
        document.querySelector(".movie-genre-container").innerHTML = genreUrl || "Không rõ";
        document.querySelector(".score-description").textContent = getScoreDescription(7)|| "Không có mô tả";


        // 4. Hiển thị video (YouTube trailer)
        const iframe = document.getElementById("trailer-player");
        if (movie.video_url) {
            iframe.src = movie.video_url
            
        } else {
            videoSection.innerHTML = "<p>Không tìm thấy video trailer.</p>";
        }

        // 5. Hiển thị điểm số
        const scoreElement = document.querySelector(".score");
        if (scoreElement) {
            scoreElement.textContent = `Score: ${movie.score || "N/A"}`;
        }

    } catch (error) {
        console.error("Lỗi khi lấy chi tiết phim:", error);
        document.querySelector(".movie-title").textContent = "Đã xảy ra lỗi khi tải dữ liệu.";
    }
});



