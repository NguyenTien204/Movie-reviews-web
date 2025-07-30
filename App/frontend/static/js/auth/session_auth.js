// session.js

// Kiểm tra user đã login chưa
window.isLoggedIn = function() {
    return localStorage.getItem('authToken') !== null;
};

// Đăng xuất
window.logout = function() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userInfo');
    window.location.reload();
    console.log('User logged out');
};

// Lấy thông tin user hiện tại
window.getCurrentUser = function() {
    const userInfo = localStorage.getItem('userInfo');
    return userInfo ? JSON.parse(userInfo) : null;
};

// Lấy token hiện tại
window.getAuthToken = function() {
    return localStorage.getItem('authToken');
};
