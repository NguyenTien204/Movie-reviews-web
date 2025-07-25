// Initialize carousels when DOM is loaded
document.addEventListener('DOMContentLoaded', async function() {
    // Show loading state
    const featuredContainer = document.getElementById('featured-grid');
    const trendingContainer = document.getElementById('trending-grid');
    
    if (featuredContainer) featuredContainer.innerHTML = '<div class="loading">Loading featured movies...</div>';
    if (trendingContainer) trendingContainer.innerHTML = '<div class="loading">Loading trending movies...</div>';

    try {
        // Fetch data from API
        const [featuredMoviesData, trendingMoviesData] = await Promise.all([
            fetchFeaturedMovies(),
            fetchTrendingMovies()
        ]);
        console.log('Featured Movies:', featuredMoviesData);
        console.log('Trending Movies:', trendingMoviesData);
        // Initialize carousels with responsive settings
        const featuredCarousel = new MovieCarousel('featured-grid', 4, 280, 20);
        const trendingCarousel = new MovieCarousel('trending-grid', 7, 159, 40);

        // Setup carousels with API data
        if (featuredMoviesData && featuredMoviesData.length > 0) {
            featuredCarousel.init(featuredMoviesData, 'movie-card');
        } else {
            if (featuredContainer) featuredContainer.innerHTML = '<div class="error">No featured movies available</div>';
        }

        if (trendingMoviesData && trendingMoviesData.length > 0) {
            trendingCarousel.init(trendingMoviesData, 'small-movie-card');
        } else {
            if (trendingContainer) trendingContainer.innerHTML = '<div class="error">No trending movies available</div>';
        }

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
                featuredCarousel.updateSettings(2, 180);
                trendingCarousel.updateSettings(3, 120);
            } else if (screenWidth <= 768) {
                featuredCarousel.updateSettings(3, 200);
                trendingCarousel.updateSettings(5, 140);
            } else {
                featuredCarousel.updateSettings(4, 280);
                trendingCarousel.updateSettings(6, 159);
            }
        }

        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(handleResize, 250);
        });

        handleResize();

    } catch (error) {
        console.error('Error initializing movie carousels:', error);
        if (featuredContainer) featuredContainer.innerHTML = '<div class="error">Error loading movies</div>';
        if (trendingContainer) trendingContainer.innerHTML = '<div class="error">Error loading movies</div>';
    }
});