/**
 * Cookie & Session Manager (fixed version)
 * Lưu access_token đúng chuẩn cho backend đọc
 * Sửa lỗi essentialUserData khai báo sau khi dùng
 */

// Cookie utility functions for temporary data storage
const CookieManager = {
    // Set cookie with expiration (in hours)
    set(name, value, hours = 24) {
        const expires = new Date();
        expires.setTime(expires.getTime() + (hours * 60 * 60 * 1000));
        document.cookie = `${name}=${encodeURIComponent(value)};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
    },

    // Get cookie value
    get(name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for (let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) === 0) {
                return decodeURIComponent(c.substring(nameEQ.length, c.length));
            }
        }
        return null;
    },

    // Delete cookie
    delete(name) {
        document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;`;
    },

    // Check if cookie exists
    exists(name) {
        return this.get(name) !== null;
    },

    // Set multiple cookies at once
    setMultiple(cookieObj, hours = 24) {
        Object.keys(cookieObj).forEach(key => {
            this.set(key, cookieObj[key], hours);
        });
    },

    // Get multiple cookies at once
    getMultiple(names) {
        const result = {};
        names.forEach(name => {
            result[name] = this.get(name);
        });
        return result;
    }
};

// Session management for temporary data
const SessionManager = {
    // ✅ Save login state (expires in 8 hours)
    saveLoginState(token, userInfo) {
        // 🔥 Đổi sang access_token cho backend đọc
        CookieManager.set('access_token', token, 8);

        // ✅ Khai báo trước khi dùng
        const essentialUserData = {
            email: userInfo.email,
            username: userInfo.username,
            id: userInfo.id || null
        };

        CookieManager.set('user_data', JSON.stringify(essentialUserData), 8);
        console.log('[SessionManager] ✅ Saved access_token + user_data', essentialUserData);
    },

    // Get login state
    getLoginState() {
        const token = CookieManager.get('access_token'); // ✅ lấy access_token thay vì auth_token
        const userDataStr = CookieManager.get('user_data');

        if (!token || !userDataStr) return null;

        try {
            return {
                token: token,
                user: JSON.parse(userDataStr)
            };
        } catch (e) {
            console.warn('Invalid user data in cookie');
            this.clearLoginState();
            return null;
        }
    },

    // Clear login state
    clearLoginState() {
        CookieManager.delete('access_token');
        CookieManager.delete('user_data');
    },

    // Save last visited page (expires in 2 hours)
    saveLastPage(url = window.location.href, title = document.title) {
        const pageData = {
            url: url,
            title: title.substring(0, 50),
            timestamp: Date.now()
        };
        CookieManager.set('last_page', JSON.stringify(pageData), 2);
    },

    // Get last visited page
    getLastPage() {
        const pageDataStr = CookieManager.get('last_page');
        if (!pageDataStr) return null;

        try {
            const pageData = JSON.parse(pageDataStr);
            if (Date.now() - pageData.timestamp > 2 * 60 * 60 * 1000) {
                CookieManager.delete('last_page');
                return null;
            }
            return pageData;
        } catch (e) {
            CookieManager.delete('last_page');
            return null;
        }
    },

    // Save form data temporarily (expires in 30 minutes)
    saveFormData(formId, data) {
        const formData = {
            data: data,
            timestamp: Date.now()
        };
        CookieManager.set(`form_${formId}`, JSON.stringify(formData), 0.5);
    },

    // Get form data
    getFormData(formId) {
        const formDataStr = CookieManager.get(`form_${formId}`);
        if (!formDataStr) return null;

        try {
            const formData = JSON.parse(formDataStr);
            if (Date.now() - formData.timestamp > 30 * 60 * 1000) {
                CookieManager.delete(`form_${formId}`);
                return null;
            }
            return formData.data;
        } catch (e) {
            CookieManager.delete(`form_${formId}`);
            return null;
        }
    },

    // Clear form data
    clearFormData(formId) {
        CookieManager.delete(`form_${formId}`);
    },

    // Save user preferences (expires in 30 days)
    savePreferences(prefs) {
        const essentialPrefs = {
            theme: prefs.theme || 'light',
            language: prefs.language || 'en',
            rememberMe: prefs.rememberMe || false
        };
        CookieManager.set('user_prefs', JSON.stringify(essentialPrefs), 24 * 30);
    },

    // Get user preferences
    getPreferences() {
        const prefsStr = CookieManager.get('user_prefs');
        if (!prefsStr) return { theme: 'light', language: 'en', rememberMe: false };

        try {
            return JSON.parse(prefsStr);
        } catch (e) {
            return { theme: 'light', language: 'en', rememberMe: false };
        }
    },

    // Clean expired temporary data
    cleanExpiredData() {
        const cookies = document.cookie.split(';');
        cookies.forEach(cookie => {
            const name = cookie.split('=')[0].trim();
            if (name.startsWith('temp_') || name.startsWith('form_')) {
                const value = CookieManager.get(name);
                if (value) {
                    try {
                        const data = JSON.parse(value);
                        if (data.timestamp && Date.now() - data.timestamp > 60 * 60 * 1000) {
                            CookieManager.delete(name);
                        }
                    } catch (e) {
                        CookieManager.delete(name);
                    }
                }
            }
        });
    }
};

// Global utility functions
window.SessionManager = SessionManager;
window.CookieManager = CookieManager;

// ✅ New helper to get access_token easily
window.getAccessToken = function() {
    const loginState = SessionManager.getLoginState();
    return loginState ? loginState.token : null;
};

// Check login state
window.isLoggedIn = function() {
    const loginState = SessionManager.getLoginState();
    return loginState !== null && loginState.token !== null;
};

// Logout function
window.logout = function() {
    SessionManager.clearLoginState();
    SessionManager.cleanExpiredData();
    console.log('User logged out');
    if (window.location.pathname !== '/login') {
        window.location.reload();
    }
};

// Get current user
window.getCurrentUser = function() {
    const loginState = SessionManager.getLoginState();
    return loginState ? loginState.user : null;
};

// Save user preferences
window.saveUserPreferences = function(preferences) {
    SessionManager.savePreferences(preferences);
};

// Get user preferences
window.getUserPreferences = function() {
    return SessionManager.getPreferences();
};

// Manual cleanup
window.cleanExpiredData = function() {
    SessionManager.cleanExpiredData();
    console.log('Expired data cleaned');
};

// Auto cleanup every 30 minutes
setInterval(() => {
    SessionManager.cleanExpiredData();
}, 30 * 60 * 1000);

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    SessionManager.cleanExpiredData();
    SessionManager.saveLastPage();
    const loginState = SessionManager.getLoginState();
    if (loginState) {
        console.log('✅ User already logged in:', loginState.user);
        window.dispatchEvent(new CustomEvent('userLoggedIn', {
            detail: loginState
        }));
    }
});

// Export for Node environment (optional)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CookieManager, SessionManager };
}
