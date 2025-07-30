const scoreBar = document.getElementById('scoreBar');
const circleScore = document.getElementById('circleScore');
const scoreDescription = document.getElementById('scoreDescription');
const pieces = document.querySelectorAll('.piece-score-bar');

let currentScore = 0;

// Hàm lấy màu theo điểm số
function getColorClass(score) {
    if (score >= 0 && score <= 3) return 'red';
    if (score >= 4 && score <= 6) return 'yellow';
    if (score >= 7 && score <= 10) return 'green';
    return 'red';
}

function getScoreDescription(score) {
    const numScore = parseFloat(score);
    if (isNaN(numScore)) return "No rating";

    if (numScore >= 9.0) return "Universal acclaim";
    if (numScore >= 8.0) return "Generally favorable";
    if (numScore >= 7.0) return "Generally positive";
    if (numScore >= 6.0) return "Mixed reviews";
    return "Generally negative";
}

// Hàm cập nhật màu circle-score
function updateCircleColor(score) {
    const colorClass = getColorClass(score);
    circleScore.style.backgroundColor =
        colorClass === 'red' ? '#ff4444' :
            colorClass === 'yellow' ? '#ffaa00' :
                colorClass === 'green' ? '#44aa44' : '#7dd87d';
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
function showHoverEffect(hoveredIndex) {
    resetHoverClasses();

    // Lấy màu dựa trên điểm số được hover (hoveredIndex)
    const colorClass = getColorClass(hoveredIndex);

    // Áp dụng màu cho tất cả các thanh từ 0 đến hoveredIndex
    for (let i = 0; i <= hoveredIndex; i++) {
        pieces[i].classList.add(`hover-${colorClass}`);
    }
}

// Hàm hiển thị selected effect
function showSelectedEffect(selectedIndex) {
    resetSelectedClasses();

    // Lấy màu dựa trên điểm số được chọn (selectedIndex)
    const colorClass = getColorClass(selectedIndex);

    // Áp dụng màu cho tất cả các thanh từ 0 đến selectedIndex
    for (let i = 0; i <= selectedIndex; i++) {
        pieces[i].classList.add(`selected-${colorClass}`);
    }
}

// Event listeners
pieces.forEach((piece, index) => {
    // Hover effect
    piece.addEventListener('mouseenter', () => {
        showHoverEffect(index);
    });

    // Click effect
    piece.addEventListener('click', () => {
        currentScore = index;
        circleScore.textContent = currentScore;
        scoreDescription.textContent = getScoreDescription(currentScore);
        updateCircleColor(currentScore);
        showSelectedEffect(index);
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
