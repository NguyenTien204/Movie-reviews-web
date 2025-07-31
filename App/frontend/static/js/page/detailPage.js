
import { getVideoUrl } from '../utils/getUrl.js';
import { getScoreDescription,processGenres, MovieCarousel} from '../utils/createHome.js';
import  {fetchTrendingMovies}  from '../api/apiService.js';
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


        // 🎯 Gán src cho iframe như trước
        const iframe = document.querySelector(".main-video");
        iframe.src = videoUrl;

        // 🎯 Đợi iframe load xong mới attach YT.Player
        iframe.onload = () => {
            console.log("✅ Iframe loaded, attaching YT.Player");
            player = new YT.Player('trailer-player', {
                events: { 'onStateChange': onPlayerStateChange }
            });
        };

        // (các đoạn gán title, summary, genre giữ nguyên)
        document.querySelector(".detail-movie-title").textContent = movie.title || "Không có tiêu đề";
        document.querySelector(".summary").textContent = movie.overview || "Không có mô tả";
        document.querySelector(".movie-genre-container").innerHTML = processGenres(movie.genres)
            .map(genre => `<span class="movie-genre">${genre}</span>`).join('');
        document.querySelector(".score-description").textContent = getScoreDescription(7) || "Không có mô tả";

    } catch (err) {
        console.error("Lỗi khi lấy chi tiết phim:", err);
    }
});


// Initialize trending carousel when DOM is loaded
document.addEventListener('DOMContentLoaded', async function() {
    // Show loading state for trending
    const trendingContainer = document.getElementById('related-grid');

    if (trendingContainer) {
        trendingContainer.innerHTML = '<div class="loading">Loading trending movies...</div>';
    }

    try {
        // Fetch trending movies only
        const trendingMoviesData = await fetchTrendingMovies();

        // Initialize trending carousel with default settings
        const trendingCarousel = new MovieCarousel('related-grid', 7, 159, 40);

        // Setup carousel with API data
        if (trendingMoviesData && trendingMoviesData.length > 0) {
            trendingCarousel.init(trendingMoviesData, 'small-movie-card');
        } else {
            if (trendingContainer) {
                trendingContainer.innerHTML = '<div class="error">No trending movies available</div>';
            }
        }

        // Add event listeners for arrow clicks (only for trending)
        document.addEventListener('click', (e) => {
            const arrow = e.target.closest('.arrow');
            if (!arrow) return;

            const target = arrow.dataset.target;
            const direction = arrow.classList.contains('arrow-left') ? 'left' : 'right';

            if (target === 'trending') {
                trendingCarousel.scroll(direction);
            }
        });

        // Handle responsive behavior
        function handleResize() {
            const screenWidth = window.innerWidth;

            if (screenWidth <= 480) {
                trendingCarousel.updateSettings(3, 120);
            } else if (screenWidth <= 768) {
                trendingCarousel.updateSettings(5, 140);
            } else {
                trendingCarousel.updateSettings(6, 159);
            }
        }

        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(handleResize, 250);
        });

        handleResize();

    } catch (error) {
        console.error('Error initializing trending carousel:', error);
        if (trendingContainer) {
            trendingContainer.innerHTML = '<div class="error">Error loading movies</div>';
        }
    }
});





