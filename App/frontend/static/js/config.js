// API Configuration
const BASE_URL = "http://localhost:5000/api/v1";  // Cần thay nếu bạn deploy
const POSTER_BASE = "https://image.tmdb.org/t/p/w500";


const API_CONFIG = {
    FEATURED_MOVIES_URL: `${BASE_URL}/movies/trending`,  
    TRENDING_MOVIES_URL: `${BASE_URL}/movies/trending`,
    register: `${BASE_URL}/register`,
    login: `${BASE_URL}/login`,  
    POSTER_BASE_URL: POSTER_BASE
    
}
// Hàm tiện ích để build poster URL (từ code cũ)
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
            return `static/img/error_poster.png`; // Trả về poster lỗi nếu không có video
        }
    } catch (error) {
        console.error('Error fetching video URL:', error);
        return `static/img/error_poster.png`;
    }
}