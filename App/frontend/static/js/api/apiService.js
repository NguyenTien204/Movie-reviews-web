import  {API_CONFIG}  from '../api/config.js';

// API Service Functions
async function fetchMovieData(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching movie data:', error);
        return [];
    }
}

async function fetchMovieDetailData(movieId) {
    try {
        const response = await fetch(`${API_CONFIG.MOVIE_DETAIL_URL}${movieId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching movie detail data:', error);
        return null;
    }
}
// API Functions (for real backend integration)
async function makeAPIRequest(url, data) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        return {
            success: response.ok,
            status: response.status,
            data: result
        };
    } catch (error) {
        console.error('API Request Error:', error);
        return {
            success: false,
            status: 0,
            data: { message: 'Network error. Please check your connection.' }
        };
    }
}

export async function registerUser(userData) {
    return await makeAPIRequest(API_CONFIG.register, userData);
}
export async function loginUser(userData) {
    return await makeAPIRequest(API_CONFIG.login, userData);
}

export async function fetchFeaturedMovies() {
    return await fetchMovieData(API_CONFIG.FEATURED_MOVIES_URL);
}

export async function fetchTrendingMovies() {
    return await fetchMovieData(API_CONFIG.TRENDING_MOVIES_URL);
}
