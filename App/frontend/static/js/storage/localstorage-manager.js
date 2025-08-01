// storage.js - Quản lý tất cả localStorage operations

// Storage keys
const STORAGE_KEYS = {
    USER_SCORE: 'userMovieScore',
    USER_REVIEW: 'userMovieReview',
    MOVIE_DATA: 'currentMovieData',
    // Có thể thêm nhiều keys khác
};

// Generic localStorage functions
const Storage = {
    // Lưu dữ liệu vào localStorage
    set(key, value) {
        try {
            const stringValue = typeof value === 'string' ? value : JSON.stringify(value);
            localStorage.setItem(key, stringValue);
            return true;
        } catch (error) {
            console.warn(`Cannot save to localStorage (key: ${key}):`, error);
            return false;
        }
    },

    // Lấy dữ liệu từ localStorage
    get(key, defaultValue = null) {
        try {
            const value = localStorage.getItem(key);
            if (value === null) return defaultValue;

            // Thử parse JSON, nếu không được thì trả về string
            try {
                return JSON.parse(value);
            } catch {
                return value;
            }
        } catch (error) {
            console.warn(`Cannot read from localStorage (key: ${key}):`, error);
            return defaultValue;
        }
    },

    // Xóa một key khỏi localStorage
    remove(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.warn(`Cannot remove from localStorage (key: ${key}):`, error);
            return false;
        }
    },

    // Xóa tất cả keys liên quan đến app
    clear(keysArray = Object.values(STORAGE_KEYS)) {
        let success = true;
        keysArray.forEach(key => {
            if (!this.remove(key)) {
                success = false;
            }
        });
        return success;
    },

    // Kiểm tra localStorage có khả dụng không
    isAvailable() {
        try {
            const testKey = '__localStorage_test__';
            localStorage.setItem(testKey, 'test');
            localStorage.removeItem(testKey);
            return true;
        } catch {
            return false;
        }
    },

    // Lấy kích thước localStorage hiện tại (KB)
    getSize() {
        if (!this.isAvailable()) return 0;

        let total = 0;
        for (let key in localStorage) {
            if (localStorage.hasOwnProperty(key)) {
                total += localStorage[key].length + key.length;
            }
        }
        return Math.round(total / 1024 * 100) / 100; // KB với 2 decimal places
    }
};

// Specific functions cho score
const ScoreStorage = {
    // Lưu điểm số
    save(score) {
        return Storage.set(STORAGE_KEYS.USER_SCORE, score);
    },

    // Lấy điểm số đã lưu
    get() {
        const score = Storage.get(STORAGE_KEYS.USER_SCORE, 0);
        return parseInt(score, 10) || 0;
    },

    // Xóa điểm số
    clear() {
        return Storage.remove(STORAGE_KEYS.USER_SCORE);
    },

    // Kiểm tra có điểm số đã lưu không
    exists() {
        return this.get() > 0;
    }
};

// Specific functions cho review
const ReviewStorage = {
    // Lưu review data (score + text + date)
    save(reviewData) {
        const dataToSave = {
            score: reviewData.score || 0,
            text: reviewData.text || '',
            date: reviewData.date || new Date().toISOString(),
            movieId: reviewData.movieId || null
        };
        return Storage.set(STORAGE_KEYS.USER_REVIEW, dataToSave);
    },

    // Lấy review data
    get() {
        return Storage.get(STORAGE_KEYS.USER_REVIEW, {
            score: 0,
            text: '',
            date: null,
            movieId: null
        });
    },

    // Xóa review
    clear() {
        return Storage.remove(STORAGE_KEYS.USER_REVIEW);
    },

    // Kiểm tra có review không
    exists() {
        const review = this.get();
        return review.score > 0 || review.text.length > 0;
    }
};

// Specific functions cho movie data
const MovieStorage = {
    // Lưu thông tin phim hiện tại
    save(movieData) {
        return Storage.set(STORAGE_KEYS.MOVIE_DATA, movieData);
    },

    // Lấy thông tin phim
    get() {
        return Storage.get(STORAGE_KEYS.MOVIE_DATA, {
            id: null,
            title: '',
            releaseDate: '',
            poster: ''
        });
    },

    // Xóa thông tin phim
    clear() {
        return Storage.remove(STORAGE_KEYS.MOVIE_DATA);
    }
};

// Debug functions
const StorageDebug = {
    // Log tất cả data trong localStorage
    logAll() {
        if (!Storage.isAvailable()) {
            console.log('localStorage not available');
            return;
        }

        console.group('LocalStorage Debug');
        console.log('Storage size:', Storage.getSize(), 'KB');
        console.log('Score:', ScoreStorage.get());
        console.log('Review:', ReviewStorage.get());
        console.log('Movie:', MovieStorage.get());
        console.groupEnd();
    },

    // Xóa tất cả app data
    clearAll() {
        const cleared = Storage.clear();
        console.log('All app data cleared:', cleared);
        return cleared;
    }
};

// Export
export {
    Storage,
    ScoreStorage,
    ReviewStorage,
    MovieStorage,
    StorageDebug,
    STORAGE_KEYS
};
