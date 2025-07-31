import { getPosterUrl } from '../utils/getUrl.js';




export function processGenres(genres) {
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
export function getScoreDescription(score) {
    const numScore = parseFloat(score);
    if (isNaN(numScore)) return "No rating";

    if (numScore >= 9.0) return "Universal acclaim";
    if (numScore >= 8.0) return "Generally favorable";
    if (numScore >= 7.0) return "Generally positive";
    if (numScore >= 6.0) return "Mixed reviews";
    return "Generally negative";
}

// MovieCarousel Class
export class MovieCarousel {
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
        const genresHtml = processGenres(movie.genres).map(genre =>
            `<span class="movie-genre">${genre}</span>`
        ).join('');

        // Xử lý score - sử dụng từ API nếu có, không thì để placeholder
        let score = '7' ; //movie.score || movie.vote_average || 'N/A';
        const scoreDescription = score !== 'N/A' ? getScoreDescription(score) : 'No rating yet';

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
        if (!this.container) {
            console.error("Container is null. Check selector or DOM readiness.");
            return;
        }

        const section = this.container.closest('.section');
        if (!section) {
            console.error("Could not find parent section element.");
            return;
        }
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






