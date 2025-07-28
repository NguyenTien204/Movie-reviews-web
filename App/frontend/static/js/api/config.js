// API Configuration
const BASE_URL = "http://localhost:5000/api/v1";  // Cần thay nếu bạn deploy
const POSTER_BASE = "https://image.tmdb.org/t/p/w500";


export const API_CONFIG = {
    FEATURED_MOVIES_URL: `${BASE_URL}/movies/trending`,
    TRENDING_MOVIES_URL: `${BASE_URL}/movies/trending`,
    register: `${BASE_URL}/register`,
    login: `${BASE_URL}/login`,
    POSTER_BASE: POSTER_BASE,
    BASE_URL: BASE_URL

}

