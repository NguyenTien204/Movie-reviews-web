   
       const movies = [
    {
      title: "Nilou",
      image: "img/Nilou.jpg",
      genres: ["Game", "Genre"],
      score: 61,
      description: "Nilou Genshin Impact",
      reviews: "Based on 20 Critic Reviews"
    },
    {
      title: "The Flash",
      image: "img/flash.jpg",
      genres: ["Action"],
      score: 75,
      description: "The Flash Movie",
      reviews: "Based on 30 Critic Reviews"
    },
    {
      title: "The Flash",
      image: "img/flash.jpg",
      genres: ["Action"],
      score: 75,
      description: "The Flash Movie",
      reviews: "Based on 30 Critic Reviews"
    },
   
    
    ];

  const container = document.querySelector('.movies-grid');

  movies.forEach(movie => {
    const card = document.createElement('div');
    card.className = 'movie-card';
    card.innerHTML = `
      <div class="movie-image">
        <img src="${movie.image}" alt="${movie.title}" class="card-img" />
      </div>
      <div class="movie-info">
        <h3 class="movie-title">${movie.title}</h3>
        <div class="movie-genre-container">
          ${movie.genres.map( genre => `<p class="movie-genre">${genre}</p>`).join('')}
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
   
/* Trending movies*/
   const trending_movies = [
    {
      title: "Nilou",
      image: "img/Nilou.jpg",
      score: 61,
      reviews: "Generally Favorable"
    },
    {
      title: "The Flash",
      image: "img/flash.jpg",
      score: 75,
      reviews: "Generally Favorable"
    },
    {
      title: "The Flash",
      image: "img/flash.jpg",
      score: 75,
      reviews: "Generally Favorable"
    },
    {
      title: "The Flash",
      image: "img/flash.jpg",
      score: 75,
      reviews: "Generally Favorable"
    },
    {
      title: "The Flash",
      image: "img/flash.jpg",
      score: 75,
      reviews: "Generally Favorable"
    },
    {
      title: "The Flash",
      image: "img/flash.jpg",
      score: 75,
      reviews: "Generally Favorable"
    }


  ];

  const small_container = document.querySelector('.movie-list-small');

  trending_movies.forEach(movie => {
    const small_card = document.createElement('div');
    small_card.className = 'small-movie-card';
    small_card.innerHTML = `
      <img src="${movie.image}" alt="${movie.title}">
      <div class="small-movie-title">
        <h3>${movie.title}</h3>
      </div>
      <div class="small-score-box">
        <span>${movie.score}</span>
        <p>${movie.reviews}</p>
      </div>
    `;
    small_container.appendChild(small_card);
  });