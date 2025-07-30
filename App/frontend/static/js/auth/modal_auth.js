// modal.js

// DOM Elements (các phần tử liên quan đến modal)
const authModal = document.getElementById('authModal');
const registerTab = document.getElementById('registerTab');
const loginTab = document.getElementById('loginTab');
const registerForm = document.getElementById('registerForm');
const loginForm = document.getElementById('loginForm');
const closeBtn = document.getElementById('closeBtn');
const registerLink = document.querySelector('.register-link');
const loginLink = document.querySelector('.login-link');

// --- Modal functions ---
export function showModal() {
    if (authModal.style.display !== 'flex') {
        authModal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        authModal.offsetHeight; // force reflow
    }
    authModal.classList.add('active');
}

export function hideModal() {
    authModal.classList.remove('active');
    setTimeout(() => {
        authModal.style.display = 'none';
        document.body.style.overflow = 'auto';
        resetForms();
    }, 300);
}

export function resetForms() {
    registerForm.reset();
    loginForm.reset();
    hideAllMessages();
}

export function hideAllMessages() {
    document.querySelectorAll('.message').forEach(msg => {
        msg.style.display = 'none';
    });
}

// Tab switching
export function switchTab(activeTab, inactiveTab, activeForm, inactiveForm) {
    hideAllMessages();
    activeTab.classList.add('active');
    inactiveTab.classList.remove('active');
    activeForm.classList.add('active');
    inactiveForm.classList.remove('active');
}

// Utility function to show messages
export function showMessage(elementId, message, type) {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.className = `message ${type}`;
    element.style.display = 'block';
}

// Button loading state management
export function setButtonLoading(button, isLoading) {
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

// --- Modal event listeners ---
document.addEventListener('DOMContentLoaded', function() {
    // Mở modal qua link Register
    if (registerLink) {
        registerLink.addEventListener('click', (e) => {
            e.preventDefault();
            showModal();
            switchTab(registerTab, loginTab, registerForm, loginForm);
        });
    }

    // Mở modal qua link Login
    if (loginLink) {
        loginLink.addEventListener('click', (e) => {
            e.preventDefault();
            showModal();
            switchTab(loginTab, registerTab, loginForm, registerForm);
        });
    }

    // Chuyển tab
    registerTab.addEventListener('click', () => {
        switchTab(registerTab, loginTab, registerForm, loginForm);
    });

    loginTab.addEventListener('click', () => {
        switchTab(loginTab, registerTab, loginForm, registerForm);
    });

    // Đóng modal
    closeBtn.addEventListener('click', hideModal);

    authModal.addEventListener('click', (e) => {
        if (e.target === authModal) hideModal();
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && authModal.classList.contains('active')) {
            hideModal();
        }
    });
});

// Global functions (để HTML gọi trực tiếp)
window.openLoginModal = function() {
    showModal();
    switchTab(loginTab, registerTab, loginForm, registerForm);
};

window.openRegisterModal = function() {
    showModal();
    switchTab(registerTab, loginTab, registerForm, loginForm);
};
