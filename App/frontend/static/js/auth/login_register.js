// auth.js
import { showMessage, hideAllMessages, setButtonLoading, switchTab, hideModal } from '../auth/modal_auth.js';

// API Configuration
const API_BASE_URL = 'http://localhost:5000/api/v1';

// --- API Functions ---
export async function registerUser(userData) {
    try {
        const response = await fetch(`${API_BASE_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });

        const data = await response.json();
        return { success: response.ok, status: response.status, data };
    } catch (error) {
        console.error('Registration API error:', error);
        return { success: false, status: 500, data: { message: 'Network error. Please try again.' }};
    }
}

export async function loginUser(userData) {
    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });

        const data = await response.json();

        if (response.ok && data.access_token) {
            SessionManager.saveLoginState(data.access_token, {
                email: userData.email,
                username: data.username || userData.email.split('@')[0],
                id: data.id || null
            });
        }

        return { success: response.ok, status: response.status, data };
    } catch (error) {
        console.error('Login API error:', error);
        return { success: false, status: 500, data: { message: 'Network error. Please try again.' }};
    }
}

// --- Form listeners ---
document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    const loginForm = document.getElementById('loginForm');
    const loginTab = document.getElementById('loginTab');
    const registerTab = document.getElementById('registerTab');

    // Xử lý Register Form
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideAllMessages();

        const submitButton = registerForm.querySelector('.submit-btn') || registerForm.querySelector('button[type="submit"]');
        const email = document.getElementById('registerEmail').value.trim();
        const username = document.getElementById('registerUsername').value.trim();
        const password = document.getElementById('registerPassword').value;

        // Validation
        if (!email || !username || !password) {
            showMessage('registerMessage', 'Please fill in all fields.', 'error');
            return;
        }
        if (username.length > 15 || !/^[a-zA-Z0-9]+$/.test(username)) {
            showMessage('registerMessage', 'Username must be 15 characters max, letters and numbers only.', 'error');
            return;
        }
        if (password.length < 6) {
            showMessage('registerMessage', 'Password must be at least 6 characters long.', 'error');
            return;
        }
        if (!/(?=.*\d)(?=.*[!@#$%^&*])/.test(password)) {
            showMessage('registerMessage', 'Password must contain at least 1 number and 1 special character.', 'error');
            return;
        }

        // Loading
        if (submitButton) setButtonLoading(submitButton, true);

        try {
            const result = await registerUser({ email, username, password });

            if (result.success) {
                showMessage('registerMessage', result.data.message || 'Registration successful! Please check your email.', 'success');
                setTimeout(() => {
                    switchTab(loginTab, registerTab, loginForm, registerForm);
                    document.getElementById('loginEmail').value = email;
                }, 2000);
            } else {
                let errorMessage = 'Registration failed. Please try again.';
                if (result.status === 400) errorMessage = result.data.message || 'Invalid input data.';
                else if (result.status === 409) errorMessage = 'Email or username already exists.';
                else if (result.status === 422) errorMessage = result.data.message || 'Please check your input data.';
                else if (result.data.message) errorMessage = result.data.message;

                showMessage('registerMessage', errorMessage, 'error');
            }
        } catch (error) {
            console.error('Registration error:', error);
            showMessage('registerMessage', 'An unexpected error occurred. Please try again.', 'error');
        } finally {
            if (submitButton) setButtonLoading(submitButton, false);
        }
    });

    // Xử lý Login Form
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideAllMessages();

        const submitButton = loginForm.querySelector('.submit-btn') || loginForm.querySelector('button[type="submit"]');
        const email = document.getElementById('loginEmail').value.trim();
        const password = document.getElementById('loginPassword').value;

        // Validation
        if (!email || !password) {
            showMessage('loginMessage', 'Please fill in all fields.', 'error');
            return;
        }

        if (submitButton) setButtonLoading(submitButton, true);

        try {
            const result = await loginUser({ email, password });

            if (result.success) {
                showMessage('loginMessage', 'Login successful! Redirecting...', 'success');

                if (result.data.token) localStorage.setItem('authToken', result.data.token);
                if (result.data.user) localStorage.setItem('userInfo', JSON.stringify(result.data.user));

                setTimeout(() => {
                    hideModal();
                    window.location.reload();
                }, 1500);
            } else {
                let errorMessage = 'Login failed. Please try again.';
                if (result.status === 401) errorMessage = 'Invalid email or password.';
                else if (result.status === 404) errorMessage = 'Account not found.';
                else if (result.status === 403) errorMessage = result.data.message || 'Account not verified or suspended.';
                else if (result.data.message) errorMessage = result.data.message;

                showMessage('loginMessage', errorMessage, 'error');
            }
        } catch (error) {
            console.error('Login error:', error);
            showMessage('loginMessage', 'An unexpected error occurred. Please try again.', 'error');
        } finally {
            if (submitButton) setButtonLoading(submitButton, false);
        }
    });

    // Real-time validation
    const usernameField = document.getElementById('registerUsername');
    const passwordField = document.getElementById('registerPassword');

    if (usernameField) {
        usernameField.addEventListener('input', (e) => {
            const username = e.target.value;
            e.target.style.borderColor = (username.length > 15 || !/^[a-zA-Z0-9]*$/.test(username)) ? '#dc3545' : '#ddd';
        });
    }

    if (passwordField) {
        passwordField.addEventListener('input', (e) => {
            const password = e.target.value;
            const isValid = password.length >= 6 && /(?=.*\d)(?=.*[!@#$%^&*])/.test(password);
            e.target.style.borderColor = password && !isValid ? '#dc3545' : '#ddd';
        });
    }
});
