import { ScoreBar, getCurrentScore, setGlobalScore } from '../utils/scoreBar.js';

let modalScoreBar = null;

// Hàm mở modal
function openModal() {
    const modalOverlay = document.getElementById('modalOverlay');
    if (!modalOverlay) return;

    modalOverlay.classList.add('show');
    document.body.style.overflow = 'hidden';

    // Khởi tạo score bar trong modal
    initModalScoreBar();
}

// Hàm đóng modal
function closeModal(event) {
    // Kiểm tra xem có phải click vào overlay hoặc nút close không
    if (event && event.target !== event.currentTarget && !event.target.classList.contains('close-btn')) {
        return;
    }

    const modalOverlay = document.getElementById('modalOverlay');
    if (!modalOverlay) return;

    modalOverlay.classList.remove('show');
    document.body.style.overflow = 'auto';

    // Reset form
    resetModalForm();
}

// Khởi tạo score bar trong modal
function initModalScoreBar() {
    if (modalScoreBar) {
        modalScoreBar.destroy();
    }

    modalScoreBar = ScoreBar({
        containerSelector: '#ratingSegments',
        circleSelector: '#scoreCircle',
        descriptionSelector: '#scoreText',
        maxScore: 10,
        segmentClass: 'piece-score-bar',
        hoverEffect: true,
        onClick: (score) => {
            checkFormValidity();
        }
    });

    modalScoreBar.init();

    // Sync với score hiện tại từ main component
    const currentScore = getCurrentScore();
    if (currentScore > 0) {
        modalScoreBar.setScore(currentScore);
    }
}

// Reset form trong modal
function resetModalForm() {
    // Reset score
    setGlobalScore(0);

    // Reset textarea
    const reviewText = document.getElementById('reviewText');
    if (reviewText) {
        reviewText.value = '';
        updateCharacterCount(reviewText);
    }

    // Reset score display
    const scoreCircle = document.getElementById('scoreCircle');
    const scoreText = document.getElementById('scoreText');

    if (scoreCircle) {
        scoreCircle.textContent = '0';
        scoreCircle.classList.remove('red', 'yellow', 'green');
    }

    if (scoreText) {
        scoreText.textContent = 'Select a rating';
    }
}

// Hàm đếm ký tự review
function updateCharacterCount(textarea) {
    const currentLength = textarea.value.length;
    const remaining = 5000 - currentLength;
    const minCharInfo = document.getElementById('minCharInfo');
    const charCount = document.getElementById('charCount');

    if (charCount) {
        charCount.textContent = remaining + ' characters remaining';
    }

    if (minCharInfo) {
        if (currentLength < 75) {
            const needed = 75 - currentLength;
            minCharInfo.textContent = `Minimum ${needed} characters needed`;
            minCharInfo.className = 'char-requirement needed';
        } else {
            minCharInfo.textContent = 'Minimum requirement met ✓';
            minCharInfo.className = 'char-requirement met';
        }
    }

    checkFormValidity();
}

// Kiểm tra form hợp lệ
function checkFormValidity() {
    const reviewText = document.getElementById('reviewText');
    const postBtn = document.getElementById('postBtn');

    if (!reviewText || !postBtn) return;

    const currentScore = getCurrentScore();
    const isValid = currentScore > 0 && reviewText.value.length >= 75;

    postBtn.disabled = !isValid;
}

// Submit review
function submitReview() {
    const reviewText = document.getElementById('reviewText');
    const currentScore = getCurrentScore();

    if (!reviewText) return;

    if (currentScore > 0 && reviewText.value.length >= 75) {
        alert(`Review submitted!\nScore: ${currentScore}/10\nReview: ${reviewText.value.substring(0, 100)}...`);
        closeModal();
    }
}

// Event listeners
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeModal();
    }
});

// Export functions để có thể gọi từ HTML
window.openModal = openModal;
window.closeModal = closeModal;
window.updateCharacterCount = updateCharacterCount;
window.submitReview = submitReview;

export { openModal, closeModal, updateCharacterCount, submitReview };
