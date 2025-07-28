import  {API_CONFIG}  from '../api/config.js';


export function getPosterUrl(path) {
    return path ? `${API_CONFIG.POSTER_BASE}${path}` : `${API_CONFIG.POSTER_BASE}/c32TsWLES7kL1uy6fF03V67AIYX.jpg`;
}

export async function getVideoUrl(movieId) {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/movies/${movieId}/trailer`);
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


