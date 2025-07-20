// API Configuration
const BASE_URL = "http://localhost:5000/api/v1";  // Cần thay nếu bạn deploy
const POSTER_BASE = "https://image.tmdb.org/t/p/w500";

const API_CONFIG = {
    FEATURED_MOVIES_URL: `${BASE_URL}/movies/trending`,  // Sử dụng endpoint từ code cũ
    TRENDING_MOVIES_URL: `${BASE_URL}/movies/trending`,  // Hoặc có thể khác nếu bạn có endpoint riêng
    POSTER_BASE_URL: POSTER_BASE
};

// Hàm tiện ích để build poster URL (từ code cũ)
function getPosterUrl(path) {
    return path ? `${POSTER_BASE}${path}` : `${POSTER_BASE}/c32TsWLES7kL1uy6fF03V67AIYX.jpg`;
}

// API Service Functions
async function fetchMovieData(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching movie data:', error);
        return [];
    }
}

async function fetchFeaturedMovies() {
    return await fetchMovieData(API_CONFIG.FEATURED_MOVIES_URL);
}

async function fetchTrendingMovies() {
    return await fetchMovieData(API_CONFIG.TRENDING_MOVIES_URL);
}

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
        const score = movie.score || movie.vote_average || 'N/A';
        const scoreDescription = score !== 'N/A' ? this.getScoreDescription(score) : 'No rating yet';

        return `
            <div class="movie-card">
                <div class="movie-image">
                    <img src="${imageUrl}" alt="${movie.title}" loading="lazy">
                </div>
                <div class="movie-info">
                    <h3 class="movie-title">${movie.title}</h3>
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
                <div class="small-movie-title">${movie.title}</div>
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

// Initialize carousels when DOM is loaded
document.addEventListener('DOMContentLoaded', async function() {
    // Show loading state
    const featuredContainer = document.getElementById('featured-grid');
    const trendingContainer = document.getElementById('trending-grid');
    
    if (featuredContainer) featuredContainer.innerHTML = '<div class="loading">Loading featured movies...</div>';
    if (trendingContainer) trendingContainer.innerHTML = '<div class="loading">Loading trending movies...</div>';

    try {
        // Fetch data from API
        const [featuredMoviesData, trendingMoviesData] = await Promise.all([
            fetchFeaturedMovies(),
            fetchTrendingMovies()
        ]);

        // Initialize carousels with responsive settings
        const featuredCarousel = new MovieCarousel('featured-grid', 4, 280, 20);
        const trendingCarousel = new MovieCarousel('trending-grid', 7, 159, 40);

        // Setup carousels with API data
        if (featuredMoviesData && featuredMoviesData.length > 0) {
            featuredCarousel.init(featuredMoviesData, 'movie-card');
        } else {
            if (featuredContainer) featuredContainer.innerHTML = '<div class="error">No featured movies available</div>';
        }

        if (trendingMoviesData && trendingMoviesData.length > 0) {
            trendingCarousel.init(trendingMoviesData, 'small-movie-card');
        } else {
            if (trendingContainer) trendingContainer.innerHTML = '<div class="error">No trending movies available</div>';
        }

        // Add event listeners for arrow clicks
        document.addEventListener('click', (e) => {
            const arrow = e.target.closest('.arrow');
            if (!arrow) return;
            
            const target = arrow.dataset.target;
            const direction = arrow.classList.contains('arrow-left') ? 'left' : 'right';
            
            if (target === 'featured') {
                featuredCarousel.scroll(direction);
            } else if (target === 'trending') {
                trendingCarousel.scroll(direction);
            }
        });

        // Handle responsive behavior
        function handleResize() {
            const screenWidth = window.innerWidth;
            
            if (screenWidth <= 480) {
                featuredCarousel.updateSettings(2, 180);
                trendingCarousel.updateSettings(3, 120);
            } else if (screenWidth <= 768) {
                featuredCarousel.updateSettings(3, 200);
                trendingCarousel.updateSettings(5, 140);
            } else {
                featuredCarousel.updateSettings(4, 280);
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
        console.error('Error initializing movie carousels:', error);
        if (featuredContainer) featuredContainer.innerHTML = '<div class="error">Error loading movies</div>';
        if (trendingContainer) trendingContainer.innerHTML = '<div class="error">Error loading movies</div>';
    }
});

// Video function - giữ nguyên
function changeVideo(src, title, desc, poster, score) {
    const iframe = document.getElementById("main-video");
    const videoTitle = document.getElementById("video-title");
    const videoDesc = document.getElementById("video-desc");
    const scoreBox = document.querySelector(".score-box");
    const metaScore = document.querySelector(".meta-label");

    let videoId = "";
    if (src.includes("watch?v=")) {
        videoId = src.split("watch?v=")[1];
    } else if (src.includes("youtu.be/")) {
        videoId = src.split("youtu.be/")[1];
    } else {
        videoId = src;
    }

    iframe.src = `https://www.youtube.com/embed/${videoId}?autoplay=1`;

    videoTitle.textContent = title;
    metaScore.textContent = "METASCORE";
    videoDesc.textContent = desc;
    scoreBox.textContent = score;
}

window.changeVideo = changeVideo;

// Export for use in other modules (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { MovieCarousel };
}