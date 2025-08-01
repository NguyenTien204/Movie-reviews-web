import { getScoreDescription } from '../utils/createHome.js';

// Global state để chia sẻ giữa các component
let globalCurrentScore = 0;
let callbacks = []; // Danh sách các callback khi score thay đổi

// Hàm đăng ký callback khi score thay đổi
function onScoreChange(callback) {
    callbacks.push(callback);
}

// Hàm thông báo score đã thay đổi
function notifyScoreChange(score) {
    globalCurrentScore = score;
    callbacks.forEach(callback => callback(score));
}

// Hàm lấy score hiện tại
function getCurrentScore() {
    return globalCurrentScore;
}

// Hàm set score từ bên ngoài
function setGlobalScore(score) {
    if (score >= 0 && score <= 10) {
        notifyScoreChange(score);
    }
}

// Hàm trả về màu dựa trên điểm
function getScoreColor(score) {
    if (score >= 1 && score <= 3) return 'red';
    if (score >= 4 && score <= 6) return 'yellow';
    if (score >= 7 && score <= 10) return 'green';
    return 'inactive';
}

// Hàm trả về class dùng cho text hoặc score circle
function getScoreClass(score) {
    if (score >= 1 && score <= 3) return 'red';
    if (score >= 4 && score <= 6) return 'yellow';
    if (score >= 7 && score <= 10) return 'green';
    return '';
}

// Class ScoreBar có thể tái sử dụng
function ScoreBar(config) {
    const {
        containerSelector,
        circleSelector,
        descriptionSelector,
        maxScore = 10,
        segmentClass = 'piece-score-bar',
        hoverEffect = true,
        onClick = null
    } = config;

    let container = document.querySelector(containerSelector);
    let circleEl = document.querySelector(circleSelector);
    let descriptionEl = document.querySelector(descriptionSelector);
    let pieces = [];
    let currentScore = 0;
    let hoveredScore = 0;

    // Tạo các piece/segment
    function createPieces() {
        if (!container) return;

        container.innerHTML = '';
        pieces = [];

        for (let i = 1; i <= maxScore; i++) {
            const piece = document.createElement('div');
            piece.className = `${segmentClass} piece-${i} inactive`;
            piece.setAttribute('data-score', i);

            // Event listeners
            if (hoverEffect) {
                piece.addEventListener('mouseenter', () => handleHover(i));
                piece.addEventListener('mouseleave', () => handleMouseLeave());
            }
            piece.addEventListener('click', () => handleClick(i));

            container.appendChild(piece);
            pieces.push(piece);
        }
    }

    // Update display
    function updateDisplay(score, isTemp = false) {
        updatePieces(score);
        updateCircleAndDescription(score);

        if (!isTemp) {
            currentScore = score;
            // Notify global change
            notifyScoreChange(score);
        }
    }

    // Update pieces color
    function updatePieces(score) {
        const color = getScoreColor(score);
        pieces.forEach((piece, index) => {
            const pieceScore = index + 1;
            if (pieceScore <= score) {
                piece.className = `${segmentClass} piece-${pieceScore} ${color}`;
            } else {
                piece.className = `${segmentClass} piece-${pieceScore} inactive`;
            }
        });
    }

    // Update circle and description
    function updateCircleAndDescription(score) {
        if (circleEl) {
            circleEl.textContent = score;
            circleEl.classList.remove('red', 'yellow', 'green');
            const colorClass = getScoreClass(score);
            if (colorClass) {
                circleEl.classList.add(colorClass);
            }
        }

        if (descriptionEl) {
            descriptionEl.textContent = getScoreDescription(score);
        }
    }

    // Hover handlers
    function handleHover(score) {
        if (!hoverEffect) return;
        hoveredScore = score;
        updateDisplay(score, true);
    }

    function handleMouseLeave() {
        if (!hoverEffect) return;
        hoveredScore = 0;
        updateDisplay(currentScore, true);
    }

    // Click handler
    function handleClick(score) {
        currentScore = score;
        updateDisplay(score);

        if (onClick) {
            onClick(score);
        }
    }

    // Listen to global score changes
    onScoreChange((score) => {
        if (score !== currentScore) {
            currentScore = score;
            updateDisplay(score, true);
        }
    });

    // Public methods
    return {
        init: function() {
            createPieces();
            updateDisplay(globalCurrentScore);
        },
        setScore: function(score) {
            currentScore = score;
            updateDisplay(score);
        },
        getScore: function() {
            return currentScore;
        },
        destroy: function() {
            if (container) {
                container.innerHTML = '';
            }
            pieces = [];
        }
    };
}

// Export functions
export {
    ScoreBar,
    getCurrentScore,
    setGlobalScore,
    onScoreChange,
    getScoreColor,
    getScoreClass,
    getScoreDescription
};
