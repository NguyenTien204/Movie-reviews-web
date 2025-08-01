// Thêm import storage
import { ScoreBar, getCurrentScore, setGlobalScore, initializeScore, getScoreDescription } from './scoreBar.js';
import { ReviewStorage, MovieStorage } from './storage.js';

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
        segmentClass: 'rating-segment',
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

    // Load review text đã lưu (nếu có)
    loadSavedReview();
}

// Load review đã lưu
function loadSavedReview() {
    const savedReview = ReviewStorage.get();
    const reviewText = document.getElementById('reviewText');

    if (reviewText && savedReview.text) {
        reviewText.value = savedReview.text;
        updateCharacterCount(reviewText);
    }
}

// Lưu review text khi người dùng gõ
function saveReviewText(text) {
    const currentScore = getCurrentScore();
    ReviewStorage.save({
        score: currentScore,
        text: text,
        date: new Date().toISOString()
    });
}

// Reset form trong modal (KHÔNG reset score đã lưu)
function resetModalForm() {
    // KHÔNG reset score - giữ nguyên điểm đã chọn
    // setGlobalScore(0); // ← Bỏ dòng này

    // Chỉ reset textarea
    const reviewText = document.getElementById('reviewText');
    if (reviewText) {
        reviewText.value = '';
        updateCharacterCount(reviewText);
    }

    // Xóa review text đã lưu
    ReviewStorage.clear();

    // Cập nhật display với score hiện tại (đã lưu)
    const currentScore = getCurrentScore();
    const scoreCircle = document.getElementById('scoreCircle');
    const scoreText = document.getElementById('scoreText');

    if (scoreCircle) {
        scoreCircle.textContent = currentScore || '0';
        scoreCircle.classList.remove('red', 'yellow', 'green');

        if (currentScore > 0) {
            let colorClass = '';
            if (currentScore >= 1 && currentScore <= 3) colorClass = 'red';
            else if (currentScore >= 4 && currentScore <= 6) colorClass = 'yellow';
            else if (currentScore >= 7 && currentScore <= 10) colorClass = 'green';

            if (colorClass) scoreCircle.classList.add(colorClass);
        }
    }

    if (scoreText) {
        scoreText.textContent = currentScore > 0 ? getScoreDescription(currentScore) : 'Select a rating';
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

    // Lưu review text khi người dùng gõ
    saveReviewText(textarea.value);

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
        // Lưu review hoàn chỉnh
        ReviewStorage.save({
            score: currentScore,
            text: reviewText.value,
            date: new Date().toISOString(),
            submitted: true
        });

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

export { openModal, closeModal, updateCharacterCount, submitReview, loadSavedReview, saveReviewText };
