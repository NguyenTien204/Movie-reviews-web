// DOM Elements
const authModal = document.getElementById('authModal');
const registerTab = document.getElementById('registerTab');
const loginTab = document.getElementById('loginTab');
const registerForm = document.getElementById('registerForm');
const loginForm = document.getElementById('loginForm');
const closeBtn = document.getElementById('closeBtn');
const registerLink = document.querySelector('.register-link');
const loginLink = document.querySelector('.login-link');

// Modal functions
function showModal() {
    authModal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function hideModal() {
    authModal.classList.remove('active');
    document.body.style.overflow = 'auto';
    resetForms();
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

    // Update tab appearance
    activeTab.classList.add('active');
    inactiveTab.classList.remove('active');

    // Switch forms
    activeForm.classList.add('active');
    inactiveForm.classList.remove('active');
}

// Event listeners for modal
registerLink.addEventListener('click', (e) => {
    e.preventDefault();
    showModal();
    switchTab(registerTab, loginTab, registerForm, loginForm);
});

loginLink.addEventListener('click', (e) => {
    e.preventDefault();
    showModal();
    switchTab(loginTab, registerTab, loginForm, registerForm);
});

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

// Form submissions
registerForm.addEventListener('submit', (e) => {
    e.preventDefault();
    hideAllMessages();

    const email = document.getElementById('registerEmail').value;
    const username = document.getElementById('registerUsername').value;
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

    if (password.length < 6 || !/(?=.*\d)(?=.*[!@#$%^&*])/.test(password)) {
        showMessage('registerMessage', 'Password must be at least 6 characters with 1 number and special character.', 'error');
        return;
    }

    // Simulate registration
    setTimeout(() => {
        showMessage('registerMessage', 'Registration successful! Please check your email to verify your account.', 'success');
        setTimeout(() => {
            switchTab(loginTab, registerTab, loginForm, registerForm);
            document.getElementById('loginEmail').value = email;
        }, 2000);
    }, 500);
});

loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    hideAllMessages();

    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    if (!email || !password) {
        showMessage('loginMessage', 'Please fill in all fields.', 'error');
        return;
    }

    // Simulate login (demo: test@test.com / 123456)
    setTimeout(() => {
        if (email === 'test@test.com' && password === '123456') {
            showMessage('loginMessage', 'Welcome back! Redirecting...', 'success');
            setTimeout(() => {
                hideModal();
                console.log('Login successful:', { email, password });
            }, 1500);
        } else {
            showMessage('loginMessage', 'Invalid email or password. Please try again.', 'error');
        }
    }, 500);
});

// Utility function to show messages
function showMessage(elementId, message, type) {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.className = `message ${type}`;
    element.style.display = 'block';
}

// Username validation
document.getElementById('registerUsername').addEventListener('input', (e) => {
    const username = e.target.value;
    if (username.length > 15 || (username && !/^[a-zA-Z0-9]*$/.test(username))) {
        e.target.style.borderColor = '#dc3545';
    } else {
        e.target.style.borderColor = '#ddd';
    }
});

// Password validation
document.getElementById('registerPassword').addEventListener('input', (e) => {
    const password = e.target.value;
    const isValid = password.length >= 6 && /(?=.*\d)(?=.*[!@#$%^&*])/.test(password);
    e.target.style.borderColor = password && !isValid ? '#dc3545' : '#ddd';
});