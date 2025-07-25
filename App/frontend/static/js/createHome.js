// MovieCarousel Class
class MovieCarousel {
    constructor(containerId, maxVisible, cardWidth, gap = 20) {
        this.container = document.getElementById(containerId);
        this.maxVisible = maxVisible;
        this.cardWidth = cardWidth;
        this.gap = gap;
        this.currentIndex = 0;
        this.totalCards = 0;
        this.isTransitioning = false;
    }

    init(movies, cardType) {
        this.totalCards = movies.length;
        this.renderCards(movies, cardType);
        this.updateArrows();
    }

    renderCards(movies, cardType) {
        if (!this.container) return;
        
        this.container.innerHTML = '';
        
        movies.forEach((movie, index) => {
            const card = document.createElement('div');
            card.className = cardType;
            
            if (cardType === 'movie-card') {
                card.innerHTML = this.createMovieCard(movie);
            } else {
                card.innerHTML = this.createSmallMovieCard(movie);
            }
            
            this.container.appendChild(card);
        });
    }
    
    createMovieCard(movie) {
        // Sử dụng hàm getPosterUrl từ code cũ
        const imageUrl = getPosterUrl(movie.poster_path);

        // Xử lý genres từ API data
        const genresHtml = this.processGenres(movie.genres).map(genre =>
            `<span class="movie-genre">${genre}</span>`
        ).join('');

        // Xử lý score - sử dụng từ API nếu có, không thì để placeholder
        const score = movie.score || movie.vote_average || 'N/A'; //score và vote average review_count chưa có trong data base
        const scoreDescription = score !== 'N/A' ? this.getScoreDescription(score) : 'No rating yet'; 

        return `
            <div class="movie-card">
                <div class="movie-image">
                    <img src="${imageUrl}" alt="${movie.title}" loading="lazy">
                </div>
                <div class="movie-info">
                    <h3 class="movie-title">
                        <a href="/movies?movie_id=${movie.movie_id}" data-id="${movie.movie_id}" id="detail-movie">${movie.title}</a>
                    </h3>
                    <div class="movie-genre-container">
                        ${genresHtml}
                    </div>
                    <div class="card-underline"></div>
                    <div class="meta-score-section">
                        <div class="meta-label">METASCORE</div>
                        <div class="score-container">
                            <div class="score-info">
                                <div class="score-description">${scoreDescription}</div>
                                <div class="score-details">${movie.review_count ? `Based on ${movie.review_count} reviews` : 'Based on critic reviews'}</div> 
                            </div>
                            <div class="score-box">${score}</div>
                        </div>
                        <div class="rating-bar">
                            <div class="positive-bar"></div>
                            <div class="mixed-bar"></div>
                            <div class="negative-bar"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    createSmallMovieCard(movie) {
        // Sử dụng hàm getPosterUrl từ code cũ  
        const imageUrl = getPosterUrl(movie.poster_path);

        // Xử lý score
        const score = movie.score || movie.vote_average || 'N/A';
        const scoreDescription = score !== 'N/A' ? this.getScoreDescription(score) : 'No rating';

        return `
            <div class="movie-card-small">
                <img src="${imageUrl}" alt="${movie.title}" loading="lazy">
                <div class="small-movie-title">
                    <a href="/movies?movie_id=${movie.movie_id}" class="detail-movie">${movie.title}</a>
                </div>
                <div class="small-score-box">
                    <span>${score}</span>
                    <p>${scoreDescription}</p>
                </div>
            </div>
        `;
    }

    // Helper function để xử lý genres từ API
    processGenres(genres) {
        if (!genres) return [];
        
        // Nếu genres là array of objects (như từ API mẫu)
        if (Array.isArray(genres) && genres.length > 0 && typeof genres[0] === 'object') {
            return genres.map(genre => genre.name || genre.genre_name || genre);
        }
        
        // Nếu genres là array of strings
        if (Array.isArray(genres)) {
            return genres;
        }
        
        // Nếu genres là string phân cách bởi dấu phẩy
        if (typeof genres === 'string') {
            return genres.split(',').map(g => g.trim());
        }
        
        return [];
    }

    getScoreDescription(score) {
        const numScore = parseFloat(score);
        if (isNaN(numScore)) return "No rating";
        
        if (numScore >= 9.0) return "Universal acclaim";
        if (numScore >= 8.0) return "Generally favorable";
        if (numScore >= 7.0) return "Generally positive";
        if (numScore >= 6.0) return "Mixed reviews";
        return "Generally negative";
    }

    scroll(direction) {
        if (this.isTransitioning) return;
        
        this.isTransitioning = true;
        const maxIndex = Math.max(0, this.totalCards - this.maxVisible);
        
        if (direction === 'left') {
            this.currentIndex = Math.max(0, this.currentIndex - 1);
        } else {
            this.currentIndex = Math.min(maxIndex, this.currentIndex + 1);
        }
        
        const translateX = -this.currentIndex * (this.cardWidth + this.gap);
        this.container.style.transform = `translateX(${translateX}px)`;
        
        this.updateArrows();
        
        setTimeout(() => {
            this.isTransitioning = false;
        }, 300);
    }

    updateArrows() {
        const target = this.container.closest('.section').querySelector('[data-target]').dataset.target;
        const leftArrow = document.querySelector(`[data-target="${target}"].arrow-left`);
        const rightArrow = document.querySelector(`[data-target="${target}"].arrow-right`);
        
        if (!leftArrow || !rightArrow) return;
        
        if (this.currentIndex === 0) {
            leftArrow.classList.add('disabled');
        } else {
            leftArrow.classList.remove('disabled');
        }
        
        const maxIndex = Math.max(0, this.totalCards - this.maxVisible);
        if (this.currentIndex >= maxIndex) {
            rightArrow.classList.add('disabled');
        } else {
            rightArrow.classList.remove('disabled');
        }
    }

    reset() {
        this.currentIndex = 0;
        this.container.style.transform = 'translateX(0px)';
        this.updateArrows();
    }

    updateSettings(maxVisible, cardWidth) {
        this.maxVisible = maxVisible;
        this.cardWidth = cardWidth;
        this.reset();
    }
}

// Video function - đã sửa để hoạt động với HTML hiện tại
function changeVideo(src, title, desc, poster, score) {
    const iframe = document.getElementById("main-video");
    const videoTitle = document.getElementById("video-title");
    const videoDesc = document.getElementById("video-desc");
    const scoreBox = document.querySelector(".score-box");
    const metaScore = document.querySelector(".meta-label");

    // Xử lý videoId từ src
    let videoId = "";
    if (src.includes("watch?v=")) {
        videoId = src.split("watch?v=")[1];
    } else if (src.includes("youtu.be/")) {
        videoId = src.split("youtu.be/")[1];
    } else if (src.startsWith("/")) {
        // Nếu src bắt đầu bằng "/", loại bỏ dấu "/"
        videoId = src.substring(1);
    } else {
        videoId = src;
    }

    // Cập nhật iframe
    iframe.src = `https://www.youtube.com/embed/${videoId}?autoplay=1`;

    // Cập nhật thông tin video
    videoTitle.textContent = title;
    metaScore.textContent = "METASCORE";
    videoDesc.textContent = desc;
    scoreBox.textContent = score;
}

// Thêm event listener cho tất cả video-thumb khi page load
document.addEventListener('DOMContentLoaded', function() {
    const videoThumbs = document.querySelectorAll('.video-thumb');
    
    videoThumbs.forEach(thumb => {
        thumb.addEventListener('click', function() {
            // Xóa active khỏi tất cả video items
            document.querySelectorAll(".video-list > div").forEach(item => {
                item.classList.remove("active");
            });
            
            // Thêm active cho video item chứa thumb được click
            const parentDiv = this.closest('.video-list > div');
            if (parentDiv) {
                parentDiv.classList.add("active");
            }
        });
    });
});

window.changeVideo = changeVideo;