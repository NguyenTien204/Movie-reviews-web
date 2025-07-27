// DOM Elements
const authModal = document.getElementById('authModal');
const registerTab = document.getElementById('registerTab');
const loginTab = document.getElementById('loginTab');
const registerForm = document.getElementById('registerForm');
const loginForm = document.getElementById('loginForm');
const closeBtn = document.getElementById('closeBtn');
const registerLink = document.querySelector('.register-link');
const loginLink = document.querySelector('.login-link');

// API Configuration
const API_BASE_URL = 'http://localhost:5000/api/v1';

// Modal functions
function showModal() {
    if (authModal.style.display !== 'flex') {
        authModal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        authModal.offsetHeight;
    }
    authModal.classList.add('active');
}

function hideModal() {
    authModal.classList.remove('active');
    setTimeout(() => {
        authModal.style.display = 'none';
        document.body.style.overflow = 'auto';
        resetForms();
    }, 300);
}

function resetForms() {
    registerForm.reset();
    loginForm.reset();
    hideAllMessages();
}

function hideAllMessages() {
    document.querySelectorAll('.message').forEach(msg => {
        msg.style.display = 'none';
    });
}

// Tab switching
function switchTab(activeTab, inactiveTab, activeForm, inactiveForm) {
    hideAllMessages();
    activeTab.classList.add('active');
    inactiveTab.classList.remove('active');
    activeForm.classList.add('active');
    inactiveForm.classList.remove('active');
}

// Utility function to show messages
function showMessage(elementId, message, type) {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.className = `message ${type}`;
    element.style.display = 'block';
}

// Button loading state management
function setButtonLoading(button, isLoading) {
    if (isLoading) {
        button.disabled = true;
        button.dataset.originalText = button.textContent;
        button.textContent = 'Loading...';
        button.style.opacity = '0.7';
    } else {
        button.disabled = false;
        button.textContent = button.dataset.originalText || 'Submit';
        button.style.opacity = '1';
    }
}

// API Functions
async function registerUser(userData) {
    try {
        const response = await fetch(`${API_BASE_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });

        const data = await response.json();
        return {
            success: response.ok,
            status: response.status,
            data: data
        };
    } catch (error) {
        console.error('Registration API error:', error);
        return {
            success: false,
            status: 500,
            data: { message: 'Network error. Please try again.' }
        };
    }
}

async function loginUser(userData) {
    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });

        const data = await response.json();

        if (response.ok && data.access_token) {
            // ✅ Gọi SessionManager để lưu token và thông tin user
            SessionManager.saveLoginState(data.access_token, {
                email: userData.email,
                username: data.username || userData.email.split('@')[0], // tạm lấy từ email nếu backend chưa trả username
                id: data.id || null
            });
        }

        return {
            success: response.ok,
            status: response.status,
            data: data
        };

    } catch (error) {
        console.error('Login API error:', error);
        return {
            success: false,
            status: 500,
            data: { message: 'Network error. Please try again.' }
        };
    }
}


// Event listeners setup
document.addEventListener('DOMContentLoaded', function() {
    // Event listeners for modal opening
    if (registerLink) {
        registerLink.addEventListener('click', (e) => {
            e.preventDefault();
            showModal();
            switchTab(registerTab, loginTab, registerForm, loginForm);
        });
    }

    if (loginLink) {
        loginLink.addEventListener('click', (e) => {
            e.preventDefault();
            showModal();
            switchTab(loginTab, registerTab, loginForm, registerForm);
        });
    }

    // Tab switching
    registerTab.addEventListener('click', () => {
        switchTab(registerTab, loginTab, registerForm, loginForm);
    });

    loginTab.addEventListener('click', () => {
        switchTab(loginTab, registerTab, loginForm, registerForm);
    });

    // Close modal
    closeBtn.addEventListener('click', hideModal);

    authModal.addEventListener('click', (e) => {
        if (e.target === authModal) {
            hideModal();
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && authModal.classList.contains('active')) {
            hideModal();
        }
    });

    // Register Form Submission
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideAllMessages();

        const submitButton = registerForm.querySelector('.submit-btn') || registerForm.querySelector('button[type="submit"]');
        const email = document.getElementById('registerEmail').value.trim();
        const username = document.getElementById('registerUsername').value.trim();
        const password = document.getElementById('registerPassword').value;

        // Client-side validation
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

        // Set loading state
        if (submitButton) {
            setButtonLoading(submitButton, true);
        }

        try {
            const result = await registerUser({ email, username, password });

            if (result.success) {
                showMessage('registerMessage',
                    result.data.message || 'Registration successful! Please check your email to verify your account.',
                    'success'
                );

                // Auto switch to login after successful registration
                setTimeout(() => {
                    switchTab(loginTab, registerTab, loginForm, registerForm);
                    document.getElementById('loginEmail').value = email;
                }, 2000);
            } else {
                let errorMessage = 'Registration failed. Please try again.';

                if (result.status === 400) {
                    errorMessage = result.data.message || 'Invalid input data.';
                } else if (result.status === 409) {
                    errorMessage = 'Email or username already exists.';
                } else if (result.status === 422) {
                    errorMessage = result.data.message || 'Please check your input data.';
                } else if (result.data.message) {
                    errorMessage = result.data.message;
                }

                showMessage('registerMessage', errorMessage, 'error');
            }
        } catch (error) {
            console.error('Registration error:', error);
            showMessage('registerMessage', 'An unexpected error occurred. Please try again.', 'error');
        } finally {
            if (submitButton) {
                setButtonLoading(submitButton, false);
            }
        }
    });

    // Login Form Submission
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideAllMessages();

        const submitButton = loginForm.querySelector('.submit-btn') || loginForm.querySelector('button[type="submit"]');
        const email = document.getElementById('loginEmail').value.trim();
        const password = document.getElementById('loginPassword').value;

        // Client-side validation
        if (!email || !password) {
            showMessage('loginMessage', 'Please fill in all fields.', 'error');
            return;
        }

        // Set loading state
        if (submitButton) {
            setButtonLoading(submitButton, true);
        }

        try {
            const result = await loginUser({ email, password });

            if (result.success) {
                showMessage('loginMessage', 'Login successful! Redirecting...', 'success');

                // Store token if provided
                if (result.data.token) {
                    localStorage.setItem('authToken', result.data.token);
                }

                // Store user info if provided
                if (result.data.user) {
                    localStorage.setItem('userInfo', JSON.stringify(result.data.user));
                }

                // Redirect after successful login
                setTimeout(() => {
                    hideModal();
                    window.location.reload();
                }, 1500);
            } else {
                let errorMessage = 'Login failed. Please try again.';

                if (result.status === 401) {
                    errorMessage = 'Invalid email or password.';
                } else if (result.status === 404) {
                    errorMessage = 'Account not found.';
                } else if (result.status === 403) {
                    errorMessage = result.data.message || 'Account not verified or suspended.';
                } else if (result.data.message) {
                    errorMessage = result.data.message;
                }

                showMessage('loginMessage', errorMessage, 'error');
            }
        } catch (error) {
            console.error('Login error:', error);
            showMessage('loginMessage', 'An unexpected error occurred. Please try again.', 'error');
        } finally {
            if (submitButton) {
                setButtonLoading(submitButton, false);
            }
        }
    });

    // Real-time validation
    const usernameField = document.getElementById('registerUsername');
    const passwordField = document.getElementById('registerPassword');

    if (usernameField) {
        usernameField.addEventListener('input', (e) => {
            const username = e.target.value;
            if (username.length > 15 || (username && !/^[a-zA-Z0-9]*$/.test(username))) {
                e.target.style.borderColor = '#dc3545';
            } else {
                e.target.style.borderColor = '#ddd';
            }
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

// Global functions for opening modal
window.openLoginModal = function() {
    showModal();
    switchTab(loginTab, registerTab, loginForm, registerForm);
};

window.openRegisterModal = function() {
    showModal();
    switchTab(registerTab, loginTab, registerForm, loginForm);
};

// Utility function to check if user is logged in
window.isLoggedIn = function() {
    return localStorage.getItem('authToken') !== null;
};

// Utility function to logout
window.logout = function() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userInfo');
    window.location.reload();
    console.log('User logged out');
};

// Utility function to get current user
window.getCurrentUser = function() {
    const userInfo = localStorage.getItem('userInfo');
    return userInfo ? JSON.parse(userInfo) : null;
};

// Utility function to get auth token
window.getAuthToken = function() {
    return localStorage.getItem('authToken');
};
