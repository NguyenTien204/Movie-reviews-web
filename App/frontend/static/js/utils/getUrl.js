import  {API_CONFIG}  from '../api/config.js';


export function getPosterUrl(path) {
    return path ? `${API_CONFIG.POSTER_BASE}${path}` : `${API_CONFIG.POSTER_BASE}/c32TsWLES7kL1uy6fF03V67AIYX.jpg`;
}
export function getDate(apiDate) {
    if (!apiDate) return ""; // Nếu API không trả về gì thì trả về rỗng

    const date = new Date(apiDate); // Tạo Date object từ string ISO

    // Format theo dạng "Jul 2, 2025"
    return date.toLocaleDateString("en-US", {
        month: "short",   // Jul, Aug, Sep...
        day: "numeric",   // 1, 2, 3...
        year: "numeric"   // 2025
    });
}

export async function getVideoUrl(movieId) {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/movies/${movieId}/trailer`);
        if (!response.ok) throw new Error('Failed to fetch trailer');

        const data = await response.json();
        const firstTrailer = Array.isArray(data) ? data[0] : null;
        const url = firstTrailer?.key;

        if (url) {
            return `https://www.youtube.com/embed/${url}?enablejsapi=1`;
        } else {
            return `static/img/error_poster.png`;
        }
    } catch (error) {
        console.error('Error fetching video URL:', error);
        return `static/img/error_poster.png`;
    }
}




