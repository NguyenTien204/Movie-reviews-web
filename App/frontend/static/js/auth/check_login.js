    document.addEventListener('DOMContentLoaded', () => {
    const registerButton = document.getElementById('registerButton');

    // ✅ Lấy token và user info từ cookie
    const loginState = SessionManager.getLoginState();

    if (loginState && loginState.token) {
        // Có token => đã login
        registerButton.style.display = 'none';

    } else {
        // Không có token => chưa login
        registerButton.style.display = 'inline-block';
        userIcon.style.display = 'none';
    }
});
