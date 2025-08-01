import { getScoreDescription } from '../utils/createHome.js';

const scoreBar = document.getElementById('scoreBar');
const circleScore = document.getElementById('circleScore');
const scoreDescription = document.getElementById('scoreDescription');
const pieces = document.querySelectorAll('.piece-score-bar');

let currentScore = 0; // Mặc định ban đầu là 0 (chưa chọn điểm)

// Hàm lấy màu theo điểm số
function getColorClass(score) {
    if (score >= 1 && score <= 3) return 'red';
    if (score >= 4 && score <= 6) return 'yellow';
    if (score >= 7 && score <= 10) return 'green';
    return 'inactive';
}

// Hàm cập nhật màu circle-score
function updateCircleColor(score) {
    const colorClass = getColorClass(score);
    circleScore.style.backgroundColor =
        colorClass === 'red' ? '#ff4444' :
        colorClass === 'yellow' ? '#ffaa00' :
        colorClass === 'green' ? '#7dd87d' : '#7dd87d';
}

// Hàm reset tất cả hover classes
function resetHoverClasses() {
    pieces.forEach(piece => {
        piece.classList.remove('hover-red', 'hover-yellow', 'hover-green');
    });
}

// Hàm reset tất cả selected classes
function resetSelectedClasses() {
    pieces.forEach(piece => {
        piece.classList.remove('selected-red', 'selected-yellow', 'selected-green');
    });
}

// Hàm hiển thị hover effect
function showHoverEffect(hoveredScore) {
    resetHoverClasses();
    const colorClass = getColorClass(hoveredScore);

    // Tô màu từ piece đầu tiên tới piece đang hover
    for (let i = 0; i < hoveredScore; i++) {
        pieces[i].classList.add(`hover-${colorClass}`);
    }
}

// Hàm hiển thị selected effect
function showSelectedEffect(selectedScore) {
    resetSelectedClasses();
    const colorClass = getColorClass(selectedScore);

    // Tô màu từ piece đầu tiên tới piece được chọn
    for (let i = 0; i < selectedScore; i++) {
        pieces[i].classList.add(`selected-${colorClass}`);
    }
}

// Event listeners cho từng piece
pieces.forEach((piece, index) => {
    const scoreValue = index + 1; // ✅ Fix: chuyển index (0–9) thành score (1–10)

    // Hover effect
    piece.addEventListener('mouseenter', () => {
        showHoverEffect(scoreValue);
    });

    // Click effect
    piece.addEventListener('click', () => {
        currentScore = scoreValue; // ✅ Lưu điểm đã chọn
        circleScore.textContent = currentScore;
        scoreDescription.textContent = getScoreDescription(currentScore);
        updateCircleColor(currentScore);
        showSelectedEffect(scoreValue);
    });
});

// Reset hover khi mouse leave khỏi score bar
scoreBar.addEventListener('mouseleave', () => {
    resetHoverClasses();
    if (currentScore > 0) {
        showSelectedEffect(currentScore);
    }
});

// Khởi tạo trạng thái ban đầu
circleScore.textContent = '0';
scoreDescription.textContent = getScoreDescription(0);
