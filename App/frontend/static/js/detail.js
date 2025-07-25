

// Function tạo HTML cho video section từ dữ liệu API
async function createDetailVideoHTML(movieData) {
    try {
        if (!movieData || (!movieData.movie_id)) {
            throw new Error('Invalid movie data: missing movie_id');
        }

        // Lấy video URL từ API, sử dụng movie_id hoặc id
        const movieId = movieData.movie_id ;
        console.log('Using movieId for video:', movieId);
        const videoUrl = await getVideoUrl(movieId);
        
        // Tạo HTML với video và overview
        return `
            <iframe id="main-video" 
                    src="${videoUrl}" 
                    frameborder="0" 
                    allowfullscreen
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture;"
                    style="width: 100%; height: 400px;">
            </iframe>
            <div class="summary">
                <p>${movieData.overview || 'No summary available...'}</p>
            </div>`;
    } catch (error) {
        console.error('Error creating video HTML:', error);
        // Trả về placeholder nếu có lỗi
        return `
            <div class="video-error">
                <p>Unable to load video</p>
            </div>
            <div class="summary">
                <p>${movieData.overview || 'No summary available...'}</p>
            </div>`;
    }
}

// Function tạo HTML cho rating section từ dữ liệu API
function createDetailRatingHTML(movieData) {
    // Xử lý genres từ API data
    const genresHTML = processGenres(movieData.genres).map(genre =>
        `<span class="movie-genre">${genre}</span>`
    ).join('');
    
    // Tính toán rating bar widths dựa trên score
    const score = movieData.score || movieData.vote_average || movieData.metaScore || 0;
    const numScore = parseFloat(score);
    let positiveWidth = 0, mixedWidth = 0, negativeWidth = 0;
    
    if (numScore >= 7.5) {
        positiveWidth = 70;
        mixedWidth = 20;
        negativeWidth = 10;
    } else if (numScore >= 5.0) {
        positiveWidth = 40;
        mixedWidth = 50;
        negativeWidth = 10;
    } else {
        positiveWidth = 20;
        mixedWidth = 30;
        negativeWidth = 50;
    }
    
    // Tạo score description
    function getScoreDescription(score) {
        const numScore = parseFloat(score);
        if (isNaN(numScore)) return "No rating";
        
        if (numScore >= 9.0) return "Universal acclaim";
        if (numScore >= 8.0) return "Generally favorable";
        if (numScore >= 7.0) return "Generally positive";
        if (numScore >= 6.0) return "Mixed reviews";
        return "Generally negative";
    }
    
    // Tạo my score bars
    const myScore = movieData.myScore || Math.round(numScore);
    const myScoreBars = Array.from({length: 11}, (_, i) => {
        const isActive = i <= myScore;
        return `<div class="piece-score-bar piece-${i} ${isActive ? 'active' : ''}"></div>`;
    }).join('');
    
    return `
        <h2 class = "movie-title">${movieData.title || 'Movie Title'}</h2>
        <div class="detail-underline"></div>
        <div class="meta-label">METASCORE</div>
        <div class="score-container">
            <div class="score-info">
                <div class="score-description">${getScoreDescription(score)}</div>
                <div class="score-details">Based on ${movieData.review_count || 20} Critic Reviews</div>
            </div>
            <div class="score-box">${Math.round(numScore * 10) || 71}</div>
        </div>
        <div class="rating-bar">
            <div class="positive-bar" style="width: ${positiveWidth}%"></div>
            <div class="mixed-bar" style="width: ${mixedWidth}%"></div>
            <div class="negative-bar" style="width: ${negativeWidth}%"></div>
        </div>
        <div class="detail-genre">
            <p style="color:gray;letter-spacing: 1px;">Genre</p>
            <div class="movie-genre-container">
                ${genresHTML}
            </div>
        </div>
        <div class="detail-myscore">
            <p style="color:gray; letter-spacing: 1px; margin-bottom: 5px;">MY SCORE</p>
            <div class="circle-score">${myScore}</div>
            <div class="score-description">${getScoreDescription(myScore)}</div>
            <div class="myscore-bar">
                ${myScoreBars}
            </div>
            <div class="post-myreview">
                <a href="${movieData.reviewEditUrl || '#'}">Edit My Review</a>
            </div>
        </div>`;
}

// Helper function để xử lý genres từ API (sử dụng từ code mẫu)
function processGenres(genres) {
    if (!genres) return [];
    if (Array.isArray(genres) && genres.length > 0 && typeof genres[0] === 'object') {
        return genres.map(genre => genre.name || genre.genre_name || genre);
    }
    if (Array.isArray(genres)) return genres;
    if (typeof genres === 'string') return genres.split(',').map(g => g.trim());
    return [];
}

// Function tạo HTML cho toàn bộ detail (backward compatibility)
function createMovieDetailHTML(movieData) {
    const html = `
    <div class="detail-video">
        ${createDetailVideoHTML(movieData)}
    </div>
    <div class="detail-rating">
        ${createDetailRatingHTML(movieData)}
    </div>`;
    
    return html;
}

// Function để render video section vào container riêng
async function renderDetailVideo(containerSelector, movieData) {
    const container = document.querySelector(containerSelector);
    if (container) {
        container.innerHTML = '<div class="loading">Loading video...</div>';
        const videoHTML = await createDetailVideoHTML(movieData);
        container.innerHTML = videoHTML;
    }
}

// Function để render rating section vào container riêng  
function renderDetailRating(containerSelector, movieData) {
    const container = document.querySelector(containerSelector);
    if (container) {
        container.innerHTML = createDetailRatingHTML(movieData);
    }
}

// Function để render HTML vào container (backward compatibility)
function renderMovieDetail(containerSelector, movieData) {
    const container = document.querySelector(containerSelector);
    if (container) {
        container.innerHTML = createMovieDetailHTML(movieData);
    }
}

// Function để render từng phần riêng biệt cho cấu trúc detail.html
async function renderMovieDetailSeparate(movieData) {
    await renderDetailVideo('.detail-video', movieData);
    renderDetailRating('.detail-rating', movieData);
}

// Function để fetch data từ API và render (cập nhật để sử dụng movie ID)
async function loadMovieDetail(movieId, renderType = 'separate') {
    try {
        // Show loading state
        const videoContainer = document.querySelector('.detail-video');
        const ratingContainer = document.querySelector('.detail-rating');
        
        if (videoContainer) videoContainer.innerHTML = '<div class="loading">Loading movie details...</div>';
        if (ratingContainer) ratingContainer.innerHTML = '<div class="loading">Loading ratings...</div>';

        // Fetch movie data from API
        const movieData = await fetchMovieDetailData(movieId);
        
        if (!movieData) {
            throw new Error('Movie not found');
        }

        // Render based on type
        if (renderType === 'separate') {
            renderMovieDetailSeparate(movieData);
        } else {
            renderMovieDetail(renderType, movieData);
        }

        return movieData;
    } catch (error) {
        console.error('Error loading movie detail:', error);
        
        // Show error state
        const videoContainer = document.querySelector('.detail-video');
        const ratingContainer = document.querySelector('.detail-rating');
        
        if (videoContainer) videoContainer.innerHTML = '<div class="error">Error loading movie details</div>';
        if (ratingContainer) ratingContainer.innerHTML = '<div class="error">Error loading ratings</div>';
        
        return null;
    }
}

// Function để lấy movie ID từ URL hoặc parameter và fetch từ API
function getMovieIdFromUrl() {
    // Lấy từ URL params
    const urlParams = new URLSearchParams(window.location.search);
    let movieId = urlParams.get('id') || urlParams.get('movie_id');
    
    if (!movieId) {
        // Lấy từ pathname (ví dụ: /movie/123 hoặc /detail/123)
        const path = window.location.pathname;
        console.log('Current path:', path);

        // Tìm movie_id trong URL bằng regex
        const matches = path.match(/\/(?:movies|movie|detail)\/(\d+)/);
        if (matches && matches[1]) {
            movieId = matches[1];
        } else {
            // Xử lý trường hợp đặc biệt cho /movies
            if (path === '/movies') {
                return null; // Sẽ được xử lý bởi logic lấy phim trending
            }
            // Fallback: lấy phần cuối của path
            const pathParts = path.split('/');
            const lastPart = pathParts[pathParts.length - 1];
            if (!isNaN(lastPart) && lastPart !== '') {
                movieId = lastPart;
            }
        }
    }

    // Đảm bảo movieId là string
    if (movieId) {
        movieId = movieId.toString();
    }
    
    console.log('MovieId from URL:', movieId);
    return movieId;
}

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
        const response = await fetch(`${BASE_URL}/movies/${movieId}`);
        
        if (!response.ok) {
            throw new Error("Không thể lấy dữ liệu phim.");
        }

        const movie = await response.json();
        const videoUrl = await getVideoUrl(movie.movie_id);
        const genreUrl = processGenres(movie.genres).map(genre =>`<span class="movie-genre">${genre}</span>`).join('');
        console.log('Movie data:', movie.genres);
        // 3. Hiển thị dữ liệu ra HTML
        // document.querySelector(".movie-image").src = movie.backdrop_path || "/static/img/Nilou.jpg";
        document.querySelector(".detail-movie-title").textContent = movie.title || "Không có tiêu đề";
        document.querySelector(".summary").textContent = movie.overview || "Không có mô tả";
        document.querySelector(".main-video").src = videoUrl || "Không rõ";
        document.querySelector(".movie-genre-container").innerHTML = genreUrl || "Không rõ";
        document.querySelector(".score-description").textContent = getScoreDescription(myScore)|| "Không có mô tả";
        

        // 4. Hiển thị video (YouTube trailer)
        const videoSection = document.querySelector(".video-section");
        if (movie.video_url) {
            const iframe = document.createElement("iframe");
            iframe.src = movie.video_url;
            iframe.allowFullscreen = true;
            iframe.loading = "lazy";
            videoSection.appendChild(iframe);
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

// Export functions for external use
window.loadMovieDetail = loadMovieDetail;
window.renderMovieDetailSeparate = renderMovieDetailSeparate;
window.getMovieIdFromUrl = getMovieIdFromUrl;

// Ví dụ cách sử dụng với cấu trúc detail.html:

// 1. Tự động load khi có movie ID trong URL:
// URL: /detail?id=123 hoặc /movie/123
// Code sẽ tự động detect và load

// 2. Load manual với movie ID:
// loadMovieDetail(123);

// 3. Load với dữ liệu có sẵn:
// const movieData = { title: "Movie Name", ... };
// renderMovieDetailSeparate(movieData);

/* 
Cấu trúc dữ liệu API mong đợi từ database:
{
    id: 123,
    title: "Movie Title",
    name: "Alternative Title", // fallback cho title
    trailer_url: "VIDEO_ID" or "https://youtube.com/watch?v=VIDEO_ID",
    overview: "Movie description...", // có thể gọi là summary
    score: 7.5, // có thể gọi là vote_average hoặc metaScore
    review_count: 25, // số lượng reviews
    genres: [
        {name: "Action"}, 
        {name: "Adventure"}
    ], // hoặc ["Action", "Adventure"]
    poster_path: "/path/to/poster.jpg", // path tương đối
    myScore: 8 // điểm cá nhân, optional
}
*/
// pages/detail.js


