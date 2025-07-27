/**
 * Page Cache Manager
 * Cache page content and scroll position using cookies
 * Optimized for minimal memory usage
 */

const PageCacheManager = {
    // Configuration
    config: {
        maxCacheSize: 5, // Maximum number of pages to cache
        cacheExpireHours: 1, // Cache expires after 1 hour
        scrollSaveDelay: 500, // Delay before saving scroll position
        excludeFromCache: ['/login', '/register', '/logout'], // Pages not to cache
        maxContentSize: 50000 // Max content size to cache (50KB)
    },

    // Get cache key for current page
    getCacheKey(url = window.location.pathname) {
        return `page_cache_${btoa(url).replace(/[^a-zA-Z0-9]/g, '_')}`;
    },

    // Get scroll cache key
    getScrollKey(url = window.location.pathname) {
        return `scroll_${btoa(url).replace(/[^a-zA-Z0-9]/g, '_')}`;
    },

    // Check if page should be cached
    shouldCache(url = window.location.pathname) {
        return !this.config.excludeFromCache.some(excludeUrl =>
            url.includes(excludeUrl)
        );
    },

    // Compress content to save space
    compressContent(content) {
        // Simple compression: remove extra whitespace and comments
        return content
            .replace(/\s+/g, ' ') // Replace multiple spaces with single space
            .replace(/<!--[\s\S]*?-->/g, '') // Remove HTML comments
            .replace(/\/\*[\s\S]*?\*\//g, '') // Remove CSS comments
            .trim();
    },

    // Save page content to cache
    savePage(url = window.location.pathname, content = null) {
        if (!this.shouldCache(url)) return false;

        try {
            // Get content if not provided
            if (!content) {
                const mainContent = document.querySelector('main') ||
                                 document.querySelector('.container') ||
                                 document.querySelector('#content') ||
                                 document.body;
                content = mainContent ? mainContent.innerHTML : '';
            }

            // Compress content
            const compressedContent = this.compressContent(content);

            // Check size limit
            if (compressedContent.length > this.config.maxContentSize) {
                console.warn('Page content too large to cache:', url);
                return false;
            }

            const cacheData = {
                url: url,
                content: compressedContent,
                title: document.title,
                timestamp: Date.now(),
                scrollY: window.pageYOffset || document.documentElement.scrollTop
            };

            const cacheKey = this.getCacheKey(url);
            CookieManager.set(cacheKey, JSON.stringify(cacheData), this.config.cacheExpireHours);

            // Manage cache size
            this.manageCacheSize();

            console.log('Page cached:', url);
            return true;
        } catch (error) {
            console.error('Failed to cache page:', error);
            return false;
        }
    },

    // Load page from cache
    loadPage(url = window.location.pathname) {
        if (!this.shouldCache(url)) return null;

        try {
            const cacheKey = this.getCacheKey(url);
            const cacheDataStr = CookieManager.get(cacheKey);

            if (!cacheDataStr) return null;

            const cacheData = JSON.parse(cacheDataStr);

            // Check if cache is expired
            const now = Date.now();
            const expireTime = this.config.cacheExpireHours * 60 * 60 * 1000;

            if (now - cacheData.timestamp > expireTime) {
                CookieManager.delete(cacheKey);
                return null;
            }

            console.log('Page loaded from cache:', url);
            return cacheData;
        } catch (error) {
            console.error('Failed to load page from cache:', error);
            return null;
        }
    },

    // Save scroll position
    saveScrollPosition(url = window.location.pathname) {
        if (!this.shouldCache(url)) return;

        const scrollData = {
            y: window.pageYOffset || document.documentElement.scrollTop,
            x: window.pageXOffset || document.documentElement.scrollLeft,
            timestamp: Date.now()
        };

        const scrollKey = this.getScrollKey(url);
        CookieManager.set(scrollKey, JSON.stringify(scrollData), this.config.cacheExpireHours);
    },

    // Restore scroll position
    restoreScrollPosition(url = window.location.pathname) {
        if (!this.shouldCache(url)) return;

        try {
            const scrollKey = this.getScrollKey(url);
            const scrollDataStr = CookieManager.get(scrollKey);

            if (!scrollDataStr) return;

            const scrollData = JSON.parse(scrollDataStr);

            // Check if scroll data is not too old
            const now = Date.now();
            const expireTime = this.config.cacheExpireHours * 60 * 60 * 1000;

            if (now - scrollData.timestamp > expireTime) {
                CookieManager.delete(scrollKey);
                return;
            }

            // Restore scroll position with smooth animation
            window.scrollTo({
                top: scrollData.y,
                left: scrollData.x,
                behavior: 'smooth'
            });

            console.log('Scroll position restored:', url);
        } catch (error) {
            console.error('Failed to restore scroll position:', error);
        }
    },

    // Manage cache size to prevent cookie overflow
    manageCacheSize() {
        try {
            // Get all cache cookies
            const allCookies = document.cookie.split(';');
            const cacheKeys = allCookies
                .map(cookie => cookie.split('=')[0].trim())
                .filter(key => key.startsWith('page_cache_'))
                .map(key => {
                    const data = CookieManager.get(key);
                    return data ? { key, timestamp: JSON.parse(data).timestamp } : null;
                })
                .filter(item => item !== null)
                .sort((a, b) => b.timestamp - a.timestamp); // Sort by newest first

            // Remove oldest caches if exceeding limit
            if (cacheKeys.length > this.config.maxCacheSize) {
                const toRemove = cacheKeys.slice(this.config.maxCacheSize);
                toRemove.forEach(item => {
                    CookieManager.delete(item.key);
                    console.log('Old cache removed:', item.key);
                });
            }
        } catch (error) {
            console.error('Failed to manage cache size:', error);
        }
    },

    // Clear all page caches
    clearAllCache() {
        try {
            const allCookies = document.cookie.split(';');
            allCookies.forEach(cookie => {
                const key = cookie.split('=')[0].trim();
                if (key.startsWith('page_cache_') || key.startsWith('scroll_')) {
                    CookieManager.delete(key);
                }
            });
            console.log('All page cache cleared');
        } catch (error) {
            console.error('Failed to clear cache:', error);
        }
    },

    // Clear expired caches
    clearExpiredCache() {
        try {
            const now = Date.now();
            const expireTime = this.config.cacheExpireHours * 60 * 60 * 1000;

            const allCookies = document.cookie.split(';');
            allCookies.forEach(cookie => {
                const key = cookie.split('=')[0].trim();
                if (key.startsWith('page_cache_') || key.startsWith('scroll_')) {
                    const data = CookieManager.get(key);
                    if (data) {
                        try {
                            const parsedData = JSON.parse(data);
                            if (now - parsedData.timestamp > expireTime) {
                                CookieManager.delete(key);
                                console.log('Expired cache removed:', key);
                            }
                        } catch (e) {
                            // Invalid data, remove it
                            CookieManager.delete(key);
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Failed to clear expired cache:', error);
        }
    },

    // Initialize page caching
    init() {
        let scrollTimeout;

        // Save scroll position on scroll (debounced)
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                this.saveScrollPosition();
            }, this.config.scrollSaveDelay);
        });

        // Save page before leaving
        window.addEventListener('beforeunload', () => {
            this.savePage();
        });

        // Handle page visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'hidden') {
                this.savePage();
            }
        });

        // Clear expired cache on page load
        this.clearExpiredCache();

        console.log('Page Cache Manager initialized');
    }
};

// Enhanced navigation functions
const NavigationManager = {
    // Navigate to page with cache support
    navigateTo(url, useCache = true) {
        // Save current page before navigation
        PageCacheManager.savePage();

        if (useCache) {
            const cachedPage = PageCacheManager.loadPage(url);
            if (cachedPage) {
                // Use cached page
                this.loadCachedPage(cachedPage);
                return;
            }
        }

        // Navigate normally
        window.location.href = url;
    },

    // Load cached page content
    loadCachedPage(cacheData) {
        // Update page content
        const mainContent = document.querySelector('main') ||
                           document.querySelector('.container') ||
                           document.querySelector('#content') ||
                           document.body;

        if (mainContent) {
            mainContent.innerHTML = cacheData.content;
        }

        // Update title
        document.title = cacheData.title;

        // Update URL without refresh
        if (window.history.pushState) {
            window.history.pushState({}, cacheData.title, cacheData.url);
        }

        // Restore scroll position after a short delay
        setTimeout(() => {
            PageCacheManager.restoreScrollPosition(cacheData.url);
        }, 100);

        // Trigger custom event
        window.dispatchEvent(new CustomEvent('cachedPageLoaded', {
            detail: { url: cacheData.url, fromCache: true }
        }));
    },

    // Handle back button
    handleBackButton() {
        window.addEventListener('popstate', (event) => {
            const currentUrl = window.location.pathname;
            const cachedPage = PageCacheManager.loadPage(currentUrl);

            if (cachedPage) {
                this.loadCachedPage(cachedPage);
            } else {
                // Reload page if no cache
                window.location.reload();
            }
        });
    }
};

// Global functions
window.PageCacheManager = PageCacheManager;
window.NavigationManager = NavigationManager;

// Navigation helper functions
window.navigateToWithCache = function(url) {
    NavigationManager.navigateTo(url, true);
};

window.navigateToWithoutCache = function(url) {
    NavigationManager.navigateTo(url, false);
};

window.clearPageCache = function() {
    PageCacheManager.clearAllCache();
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Wait for CookieManager to be available
    if (typeof CookieManager !== 'undefined') {
        PageCacheManager.init();
        NavigationManager.handleBackButton();

        // Restore scroll position for current page
        setTimeout(() => {
            PageCacheManager.restoreScrollPosition();
        }, 500);
    } else {
        console.error('CookieManager not found. Please include cookie-session-manager.js first.');
    }
});

// Auto cleanup every 30 minutes
setInterval(() => {
    PageCacheManager.clearExpiredCache();
}, 30 * 60 * 1000);
