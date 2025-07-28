// API Configuration
const BASE_URL = "http://localhost:5000/api/v1";  // Cần thay nếu bạn deploy
const POSTER_BASE = "https://image.tmdb.org/t/p/w500";

const API_CONFIG = {
    FEATURED_MOVIES_URL: `${BASE_URL}/movies/trending`,
    TRENDING_MOVIES_URL: `${BASE_URL}/movies/trending`,
    POSTER_BASE_URL: POSTER_BASE
};

function getPosterUrl(path) {
    return path ? `${POSTER_BASE}${path}` : `${POSTER_BASE}/c32TsWLES7kL1uy6fF03V67AIYX.jpg`;
}

async function getVideoUrl(movieId) {
    try {
        const response = await fetch(`${BASE_URL}/movies/${movieId}/trailer`);
        if (!response.ok) throw new Error('Failed to fetch trailer');
        const data = await response.json();
        const url = data[0].key
        if (url) {
            return `https://www.youtube.com/embed/${url}`;
        } else {
            return `${POSTER_BASE}/c32TsWLES7kL1uy6fF03V67AIYX.jpg`;
        }
    } catch (error) {
        console.error('Error fetching video URL:', error);
        return `${POSTER_BASE}/c32TsWLES7kL1uy6fF03V67AIYX.jpg`;
    }
}

async function fetchMovieData(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
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
        const imageUrl = getPosterUrl(movie.poster_path);
        const genresHtml = this.processGenres(movie.genres).map(genre =>
            `<span class="movie-genre">${genre}</span>`
        ).join('');
        const score = movie.score || movie.vote_average || 'N/A';
        const scoreDescription = score !== 'N/A' ? this.getScoreDescription(score) : 'No rating yet';

        return `
            <div class="movie-card">
                <div class="movie-image">
                    <img src="${imageUrl}" alt="${movie.title}" loading="lazy">
                </div>
                <div class="movie-info">
                    <h3 class="movie-title">
                        <a href="/movies?movie_id=${movie.movie_id}" class="detail-movie">${movie.title}</a>
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
        const imageUrl = getPosterUrl(movie.poster_path);
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

    processGenres(genres) {
        if (!genres) return [];
        if (Array.isArray(genres) && genres.length > 0 && typeof genres[0] === 'object') {
            return genres.map(genre => genre.name || genre.genre_name || genre);
        }
        if (Array.isArray(genres)) return genres;
        if (typeof genres === 'string') return genres.split(',').map(g => g.trim());
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
        leftArrow.classList.toggle('disabled', this.currentIndex === 0);
        const maxIndex = Math.max(0, this.totalCards - this.maxVisible);
        rightArrow.classList.toggle('disabled', this.currentIndex >= maxIndex);
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

// DOM Ready
document.addEventListener('DOMContentLoaded', async function () {
    const featuredContainer = document.getElementById('featured-grid');
    const trendingContainer = document.getElementById('trending-grid');

    if (featuredContainer) featuredContainer.innerHTML = '<div class="loading">Loading featured movies...</div>';
    if (trendingContainer) trendingContainer.innerHTML = '<div class="loading">Loading trending movies...</div>';

    try {
        const [featuredMoviesData, trendingMoviesData] = await Promise.all([
            fetchFeaturedMovies(),
            fetchTrendingMovies()
        ]);

        const featuredCarousel = new MovieCarousel('featured-grid', 4, 280, 20);
        const trendingCarousel = new MovieCarousel('trending-grid', 7, 159, 40);

        if (featuredMoviesData.length > 0) {
            featuredCarousel.init(featuredMoviesData, 'movie-card');
        } else {
            featuredContainer.innerHTML = '<div class="error">No featured movies available</div>';
        }

        if (trendingMoviesData.length > 0) {
            trendingCarousel.init(trendingMoviesData, 'small-movie-card');
        } else {
            trendingContainer.innerHTML = '<div class="error">No trending movies available</div>';
        }

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

// Video logic
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
    } else if (src.startsWith("/")) {
        videoId = src.substring(1);
    } else {
        videoId = src;
    }

    iframe.src = `https://www.youtube.com/embed/${videoId}?autoplay=1`;
    videoTitle.textContent = title;
    metaScore.textContent = "METASCORE";
    videoDesc.textContent = desc;
    scoreBox.textContent = score;
}

document.addEventListener('DOMContentLoaded', function () {
    const videoThumbs = document.querySelectorAll('.video-thumb');
    videoThumbs.forEach(thumb => {
        thumb.addEventListener('click', function () {
            document.querySelectorAll(".video-list > div").forEach(item => {
                item.classList.remove("active");
            });
            const parentDiv = this.closest('.video-list > div');
            if (parentDiv) parentDiv.classList.add("active");
        });
    });
});

window.changeVideo = changeVideo;
