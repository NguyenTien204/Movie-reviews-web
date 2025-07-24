// API Configuration
const BASE_URL = "http://localhost:5000/api/v1";  // Cần thay nếu bạn deploy
const POSTER_BASE = "https://image.tmdb.org/t/p/w500";


const API_CONFIG = {
    FEATURED_MOVIES_URL: `${BASE_URL}/movies/trending`,  // Sử dụng endpoint từ code cũ
    TRENDING_MOVIES_URL: `${BASE_URL}/movies/trending`,  // Hoặc có thể khác nếu bạn có endpoint riêng
    POSTER_BASE_URL: POSTER_BASE
    
}
// Hàm tiện ích để build poster URL (từ code cũ)
function getPosterUrl(path) {
    return path ? `${POSTER_BASE}${path}` : `${POSTER_BASE}/c32TsWLES7kL1uy6fF03V67AIYX.jpg`;
}

// Hàm lấy video URL từ API
async function getVideoUrl(movieId) {
    try {
        // Gọi API để lấy thông tin trailer
        const response = await fetch(`${BASE_URL}/movies/${movieId}/trailer`);
        if (!response.ok) {
            throw new Error('Failed to fetch trailer');
        }
        const data = await response.json();
        
        // Kiểm tra nếu có key video từ API
        if (data && data.key) {
            // Tạo URL YouTube embed
            return `https://www.youtube.com/embed/${data.key}`;
        } else {
            // Trả về ảnh poster mặc định nếu không có trailer
            return `${POSTER_BASE}/c32TsWLES7kL1uy6fF03V67AIYX.jpg`;
        }
    } catch (error) {
        console.error('Error fetching video URL:', error);
        // Trả về ảnh poster mặc định nếu có lỗi
        return `${POSTER_BASE}/c32TsWLES7kL1uy6fF03V67AIYX.jpg`;
    }
}