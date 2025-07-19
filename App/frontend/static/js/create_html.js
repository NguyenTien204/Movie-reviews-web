// Sample movie data - Replace with your Django data
const featuredMovies = [
    {
        title: "Avengers: Endgame",
        genres: ["Action", "Adventure", "Drama"],
        score: 94,
        image: "/static/img/Nilou.jpg"
    },
    {
        title: "The Dark Knight",
        genres: ["Action", "Crime", "Drama"],
        score: 87,
        image: "/static/img/GI_Ganyu_Hu_Tao_Qiqi.png"
    },
    {
        title: "Inception",
        genres: ["Action", "Sci-Fi", "Thriller"],
        score: 91,
        image: "/static/img/yoimiya.png"
    },
    {
        title: "Interstellar",
        genres: ["Adventure", "Drama", "Sci-Fi"],
        score: 89,
        image: "/static/img/kokomi.jpg"
    },
    {
        title: "Pulp Fiction",
        genres: ["Crime", "Drama"],
        score: 95,
        image: "https://via.placeholder.com/280x420/5356f2/ffffff?text=Pulp+Fiction"
    },
    {
        title: "The Matrix",
        genres: ["Action", "Sci-Fi"],
        score: 88,
        image: "https://via.placeholder.com/280x420/7212d8/ffffff?text=The+Matrix"
    }
];

const trendingMovies = [
    {
        title: "Spider-Man",
        score: 85,
        image: "/static/img/flash.jpg"
    },
    {
        title: "Batman",
        score: 82,
        image: "https://tse4.mm.bing.net/th/id/OIP.Amtb86pqYYfYzrHEv4XPnQHaEK?pid=Api&P=0&h=220"
    },
    {
        title: "Iron Man",
        score: 79,
        image: "/static/img/flash.jpg"
    },
    {
        title: "Thor",
        score: 77,
        image: "/static/img/flash.jpg"
    },
    {
        title: "Captain America",
        score: 81,
        image: "/static/img/flash.jpg"
    },
    {
        title: "Wonder Woman",
        score: 84,
        image: "/static/img/flash.jpg"
    },
    {
        title: "Aquaman",
        score: 73,
        image: "/static/img/flash.jpg"
    },
    {
        title: "Black Panther",
        score: 88,
        image: "/static/img/flash.jpg"
    },
    {
        title: "Doctor Strange",
        score: 75,
        image: "/static/img/flash.jpg"
    },
    {
        title: "Green Lantern",
        score: 65,
        image: "/static/img/flash.jpg"
    }
];

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
        const genresHtml = movie.genres.map(genre => 
            `<span class="movie-genre">${genre}</span>`
        ).join('');

        return `
            <div class="movie-image">
                <img src="${movie.image}" alt="${movie.title}" loading="lazy">
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
                            <div class="score-description">${this.getScoreDescription(movie.score)}</div>
                            <div class="score-details">Based 20 on critic reviews</div>
                        </div>
                        <div class="score-box">${movie.score}</div>
                    </div>
                    <div class="rating-bar">
                        <div class="positive-bar"></div>
                        <div class="mixed-bar"></div>
                        <div class="negative-bar"></div>
                    </div>
                </div>\ 
            </div>
        `;
    }

    createSmallMovieCard(movie) {
        return `
            <img src="${movie.image}" alt="${movie.title}" loading="lazy">
            <div class="small-movie-title">${movie.title}</div>
            <div class="small-score-box">
                <span>${movie.score}</span>
                <p>${this.getScoreDescription(movie.score)}</p>
            </div>
        `;
    }

    getScoreDescription(score) {
        if (score >= 90) return "Universal acclaim";
        if (score >= 80) return "Generally favorable";
        if (score >= 70) return "Generally positive";
        if (score >= 60) return "Mixed reviews";
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
        
        // Reset transition flag after animation completes
        setTimeout(() => {
            this.isTransitioning = false;
        }, 300);
    }

    updateArrows() {
        const target = this.container.closest('.section').querySelector('[data-target]').dataset.target;
        const leftArrow = document.querySelector(`[data-target="${target}"].arrow-left`);
        const rightArrow = document.querySelector(`[data-target="${target}"].arrow-right`);
        
        if (!leftArrow || !rightArrow) return;
        
        // Update left arrow
        if (this.currentIndex === 0) {
            leftArrow.classList.add('disabled');
        } else {
            leftArrow.classList.remove('disabled');
        }
        
        // Update right arrow
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

    // Method to update carousel settings based on screen size
    updateSettings(maxVisible, cardWidth) {
        this.maxVisible = maxVisible;
        this.cardWidth = cardWidth;
        this.reset();
    }
}

// Initialize carousels when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize carousels with responsive settings
    const featuredCarousel = new MovieCarousel('featured-grid', 4, 280, 20);
    const trendingCarousel = new MovieCarousel('trending-grid', 7, 159, 40);

    // Setup carousels with data
    featuredCarousel.init(featuredMovies, 'movie-card');
    trendingCarousel.init(trendingMovies, 'small-movie-card');

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
            // Mobile settings
            featuredCarousel.updateSettings(2, 180);
            trendingCarousel.updateSettings(3, 120);
        } else if (screenWidth <= 768) {
            // Tablet settings
            featuredCarousel.updateSettings(3, 200);
            trendingCarousel.updateSettings(5, 140);
        } else {
            // Desktop settings
            featuredCarousel.updateSettings(4, 280);
            trendingCarousel.updateSettings(6, 159);
        }
    }

    // Handle window resize with debounce
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(handleResize, 250);
    });

    // Initial resize check
    handleResize();
});

// Export for use in other modules (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { MovieCarousel, featuredMovies, trendingMovies };
}
// Function to change video source and details


function changeVideo(src, title, desc, poster, score) {
    const video = document.getElementById("main-video");
    const videoTitle = document.getElementById("video-title");
    const videoDesc = document.getElementById("video-desc");
    const scoreBox = document.querySelector(".score-box");
    const metaScore = document.querySelector(".meta-label");

    video.pause();
    video.setAttribute("src", src);
    video.setAttribute("poster", poster);
    video.load();
    videoTitle.textContent = title;
    metaScore.textContent = "METASCORE";
    videoDesc.textContent = desc;
    scoreBox.textContent = score;
    
}

// ✅ Gắn hàm vào window để gọi được từ HTML
window.changeVideo = changeVideo;
