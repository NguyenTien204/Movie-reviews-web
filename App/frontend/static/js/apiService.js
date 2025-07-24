
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

async function fetchFeaturedMovies() {
    return await fetchMovieData(API_CONFIG.FEATURED_MOVIES_URL);
}

async function fetchTrendingMovies() {
    return await fetchMovieData(API_CONFIG.TRENDING_MOVIES_URL);
}
// async function fetchMovieDetail(movieId) {
//     const url = `${API_CONFIG.BASE_URL}/movies/${movieId}`;
//     return await fetchMovieData(url);
// }
// async function fetchMovieTrailers(movieId) {
//     const url = `${API_CONFIG.BASE_URL}/movies/${movieId}/trailer`;
//     return await fetchMovieData(url);
// }