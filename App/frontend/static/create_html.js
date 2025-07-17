/**
 * FILMCRITIC - MOVIE CARD RENDERER
 * Đảm bảo hiển thị ổn định khi chuyển trang
 */

// ==================== MOVIE DATA ====================
const movies = [
  {
    title: "Nilou",
    image: "/static/img/Nilou.jpg",
    genres: ["Game", "Genre"],
    score: 61,
    description: "Nilou Genshin Impact",
    reviews: "Based on 20 Critic Reviews"
  },
  {
    title: "The Flash",
    image: "/static/img/flash.jpg",
    genres: ["Action"],
    score: 75,
    description: "The Flash Movie",
    reviews: "Based on 30 Critic Reviews"
  },
  {
    title: "The Flash",
    image: "/static/img/flash.jpg",
    genres: ["Action"],
    score: 75,
    description: "The Flash Movie",
    reviews: "Based on 30 Critic Reviews"
  },
  {
    title: "The Flash",
    image: "/static/img/flash.jpg",
    genres: ["Action"],
    score: 75,
    description: "The Flash Movie",
    reviews: "Based on 30 Critic Reviews"
  },
 
];

const trending_movies = [
  {
    title: "Nilou",
    image: "/static/img/Nilou.jpg",
    score: 61,
    reviews: "Generally Favorable"
  },
  {
    title: "The Flash",
    image: "/static/img/flash.jpg",
    score: 75,
    reviews: "Generally Favorable"
  },
  {
    title: "The Flash",
    image: "/static/img/flash.jpg",
    score: 75,
    reviews: "Generally Favorable"
  },
  {
    title: "The Flash",
    image: "/static/img/flash.jpg",
    score: 75,
    reviews: "Generally Favorable"
  },
  {
    title: "The Flash",
    image: "/static/img/flash.jpg",
    score: 75,
    reviews: "Generally Favorable"
  },
  {
    title: "The Flash",
    image: "/static/img/flash.jpg",
    score: 75,
    reviews: "Generally Favorable"
  },
  {
    title: "The Flash",
    image: "/static/img/flash.jpg",
    score: 75,
    reviews: "Generally Favorable"
  },


];

// ==================== RENDER FUNCTIONS ====================
function renderMovieCards() {
  const container = document.querySelector('.movies-grid');
  if (!container) return;

  container.innerHTML = ''; // Clear existing cards

  movies.forEach(movie => {
    const card = document.createElement('div');
    card.className = 'movie-card';
    
    card.innerHTML = `
      <div class="movie-image">
        <img src="${movie.image}" alt="${movie.title}" class="card-img" 
             onerror="this.src='/static/img/default.jpg'">
      </div>
      <div class="movie-info">
        <h3 class="movie-title">${movie.title}</h3>
        <div class="movie-genre-container">
          ${movie.genres.map(genre => `<p class="movie-genre">${genre}</p>`).join('')}
        </div>
        <div class="card-underline"></div>
        <div class="meta-score-section">
          <p class="meta-label">META SCORE</p>
          <div class="score-container">
            <div>
              <div class="score-description">${movie.description}</div>
              <div class="score-details">${movie.reviews}</div>
            </div>
            <div class="score-box"><span>${movie.score}</span></div>
          </div>
        </div>
        <div class="rating-bar">
          <div class="positive-bar"></div>
          <div class="mixed-bar"></div>
          <div class="negative-bar"></div>
        </div>
      </div>
    `;
    container.appendChild(card);
  });
}

function renderTrendingMovies() {
  const container = document.querySelector('.movie-list-small');
  if (!container) return;

  container.innerHTML = ''; // Clear existing cards

  trending_movies.forEach(movie => {
    const card = document.createElement('div');
    card.className = 'small-movie-card';
    
    card.innerHTML = `
      <img src="${movie.image}" alt="${movie.title}" 
           onerror="this.src='/static/img/default.jpg'">
      <div class="small-movie-title">
        <h3>${movie.title}</h3>
      </div>
      <div class="small-score-box">
        <span>${movie.score}</span>
        <p>${movie.reviews}</p>
      </div>
    `;
    container.appendChild(card);
  });
}

// ==================== NAVIGATION HANDLER ====================
function setupNavigation() {
  // Home logo click
  document.getElementById('home-logo')?.addEventListener('click', (e) => {
    e.preventDefault();
    window.location.href = '/home'; // Full page reload
  });

  // Category link click
  document.getElementById('category-link')?.addEventListener('click', (e) => {
    e.preventDefault();
    window.location.href = '/category'; // Full page reload
  });
}

// ==================== INITIALIZATION ====================
function initPage() {
  console.log("Initializing page...");
  
  // Render movie sections
  renderMovieCards();
  renderTrendingMovies();
  
  // Setup navigation
  setupNavigation();
}

// Start when DOM is ready
document.addEventListener('DOMContentLoaded', initPage);

// Re-init if page loaded via back/forward
window.addEventListener('pageshow', initPage);