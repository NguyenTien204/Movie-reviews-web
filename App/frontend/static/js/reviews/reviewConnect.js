import { ScoreBar, getCurrentScore, setGlobalScore, onScoreChange } from '../utils/scoreBar.js';
import './reviewForm.js'; // Import modal functionality

let mainScoreBar = null;

// Khởi tạo score bar chính (ngoài modal)
function initMainScoreBar() {
    if (mainScoreBar) {
        mainScoreBar.destroy();
    }

    mainScoreBar = ScoreBar({
        containerSelector: '#scoreBar', // ID từ HTML cũ
        circleSelector: '#circleScore', // ID từ HTML cũ
        descriptionSelector: '#scoreDescription', // ID từ HTML cũ
        maxScore: 10,
        segmentClass: 'piece-score-bar', // Class từ HTML cũ
        hoverEffect: true,
        onClick: (score) => {
            // Có thể thêm logic khác ở đây nếu cần
            console.log('Main score bar clicked:', score);
        }
    });

    mainScoreBar.init();
}

// Sync giữa main score bar và modal
onScoreChange((score) => {
    // Update main display elements
    updateMainDisplay(score);
});

// Update các element hiển thị chính
function updateMainDisplay(score) {
    const circleScore = document.getElementById('circleScore');
    const scoreDescription = document.getElementById('scoreDescription');

    if (circleScore) {
        circleScore.textContent = score;
        circleScore.classList.remove('red', 'yellow', 'green');

        // Cập nhật màu background
        let bgColor = '#e9ecef'; // default green
        if (score >= 1 && score <= 3) bgColor = '#ff4444';
        else if (score >= 4 && score <= 6) bgColor = '#ffaa00';
        else if (score >= 7 && score <= 10) bgColor = '#7dd87d';

        circleScore.style = bgColor;
    }
}

// Hàm public để set score từ bên ngoài
function setScore(score) {
    setGlobalScore(score);
}

// Hàm public để get score
function getScore() {
    return getCurrentScore();
}

// Khởi tạo khi DOM ready
document.addEventListener('DOMContentLoaded', function() {
    initMainScoreBar();
});

// Export public functions
window.setScore = setScore;
window.getScore = getScore;

export { setScore, getScore, initMainScoreBar };
