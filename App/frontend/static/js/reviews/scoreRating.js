

let currentScore = 0;
let hoveredScore = 0;

// Rating text mappings
const ratingTexts = {
    0: "Select a rating",
    1: "Terrible", 2: "Awful", 3: "Bad",
    4: "Mixed", 5: "Average",
    6: "Good", 7: "Great", 8: "Excellent", 9: "Amazing", 10: "Perfect"
};

// Initialize rating bar
function initRatingBar() {
    const segmentsContainer = document.getElementById('ratingSegments');
    segmentsContainer.innerHTML = '';

    // Create 10 segments for scores 1-10
    for (let i = 1; i <= 10; i++) {
        const segment = document.createElement('div');
        segment.className = 'rating-segment inactive';
        segment.dataset.score = i;

        segment.addEventListener('mouseenter', () => handleHover(i));
        segment.addEventListener('mouseleave', () => handleMouseLeave());
        segment.addEventListener('click', () => handleClick(i));

        segmentsContainer.appendChild(segment);
    }
}

function getScoreColor(score) {
    if (score >= 1 && score <= 3) return 'red';
    if (score >= 4 && score <= 6) return 'yellow';
    if (score >= 7 && score <= 10) return 'green';
    return 'inactive';
}

function getScoreClass(score) {
    if (score >= 1 && score <= 3) return 'red';
    if (score >= 4 && score <= 6) return 'yellow';
    if (score >= 7 && score <= 10) return 'green';
    return '';
}

function updateSegments(score, isHover = false) {
    const segments = document.querySelectorAll('.rating-segment');
    const color = getScoreColor(score);

    segments.forEach((segment, index) => {
        const segmentScore = index + 1;
        if (segmentScore <= score) {
            segment.className = `rating-segment ${color}`;
        } else {
            segment.className = 'rating-segment inactive';
        }
    });
}

function updateScoreDisplay(score) {
    const scoreCircle = document.getElementById('scoreCircle');
    const scoreText = document.getElementById('scoreText');
    const colorClass = getScoreClass(score);

    scoreCircle.textContent = score;
    scoreText.textContent = ratingTexts[score];

    // Remove all color classes
    scoreCircle.classList.remove('red', 'yellow', 'green');
    scoreText.classList.remove('red', 'yellow', 'green');

    // Add appropriate color class
    if (colorClass) {
        scoreCircle.classList.add(colorClass);
        scoreText.classList.add(colorClass);
    }
}

function handleHover(score) {
    hoveredScore = score;
    updateSegments(score, true);
    updateScoreDisplay(score);
}

function handleMouseLeave() {
    hoveredScore = 0;
    updateSegments(currentScore);
    updateScoreDisplay(currentScore);
}

function handleClick(score) {
    currentScore = score;
    updateSegments(score);
    updateScoreDisplay(score);
    checkFormValidity();
}

function openModal() {
    document.getElementById('modalOverlay').classList.add('show');
    document.body.style.overflow = 'hidden';
    initRatingBar();
}

function closeModal(event) {
    if (event && event.target !== event.currentTarget && !event.target.classList.contains('close-btn')) {
        return;
    }
    document.getElementById('modalOverlay').classList.remove('show');
    document.body.style.overflow = 'auto';

    // Reset form
    currentScore = 0;
    hoveredScore = 0;
    document.getElementById('reviewText').value = '';
    updateCharacterCount(document.getElementById('reviewText'));
    updateScoreDisplay(0);
}

function updateCharacterCount(textarea) {
    const currentLength = textarea.value.length;
    const remaining = 5000 - currentLength;
    const minCharInfo = document.getElementById('minCharInfo');
    const charCount = document.getElementById('charCount');

    charCount.textContent = remaining + ' characters remaining';

    if (currentLength < 75) {
        const needed = 75 - currentLength;
        minCharInfo.textContent = `Minimum ${needed} characters needed`;
        minCharInfo.className = 'char-requirement needed';
    } else {
        minCharInfo.textContent = 'Minimum requirement met ✓';
        minCharInfo.className = 'char-requirement met';
    }

    checkFormValidity();
}

function checkFormValidity() {
    const reviewText = document.getElementById('reviewText').value;
    const postBtn = document.getElementById('postBtn');

    const isValid = currentScore > 0 && reviewText.length >= 75;
    postBtn.disabled = !isValid;
}

function submitReview() {
    if (currentScore > 0 && document.getElementById('reviewText').value.length >= 75) {
        alert(`Review submitted!\nScore: ${currentScore}/10 (${ratingTexts[currentScore]})\nReview: ${document.getElementById('reviewText').value.substring(0, 100)}...`);
        closeModal();
    }
}

// Close modal with Escape key
document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
        closeModal();
    }
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', function () {
    initRatingBar();
});
