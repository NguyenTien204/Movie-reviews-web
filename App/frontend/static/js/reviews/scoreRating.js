import {getScoreDescription} from '../utils/createHome.js';


let currentScore = 0; // Điểm người dùng đã chọn (click)
let hoveredScore = 0; // Điểm người dùng đang hover (di chuột qua)


// Hàm khởi tạo thanh rating (10 ô)
function initRatingBar() {
    const segmentsContainer = document.getElementById('ratingSegments'); // Lấy container chứa các ô rating
    segmentsContainer.innerHTML = ''; // Xóa nội dung cũ (nếu có)

    // Tạo 10 segment tương ứng 1–10
    for (let i = 1; i <= 10; i++) {
        const segment = document.createElement('div'); // Tạo div mới cho từng segment
        segment.className = 'rating-segment inactive'; // Ban đầu có class 'inactive'
        segment.dataset.score = i; // Lưu số điểm vào attribute data-score

        // Thêm event hover: đổi màu khi rê chuột
        segment.addEventListener('mouseenter', () => handleHover(i));
        // Khi rời chuột ra khỏi segment → reset
        segment.addEventListener('mouseleave', () => handleMouseLeave());
        // Khi click → chọn điểm
        segment.addEventListener('click', () => handleClick(i));

        // Thêm segment vào container
        segmentsContainer.appendChild(segment);
    }
}

// Hàm trả về màu dựa trên điểm
function getScoreColor(score) {
    if (score >= 1 && score <= 3) return 'red';      // 1–3 → đỏ
    if (score >= 4 && score <= 6) return 'yellow';   // 4–6 → vàng
    if (score >= 7 && score <= 10) return 'green';   // 7–10 → xanh lá
    return 'inactive'; // Trường hợp không hợp lệ
}

// Hàm trả về class dùng cho text hoặc score circle
function getScoreClass(score) {
    if (score >= 1 && score <= 3) return 'red';
    if (score >= 4 && score <= 6) return 'yellow';
    if (score >= 7 && score <= 10) return 'green';
    return ''; // Không màu
}

// Hàm update màu cho thanh rating
function updateSegments(score, isHover = false) {
    const segments = document.querySelectorAll('.rating-segment'); // Lấy tất cả segment
    const color = getScoreColor(score); // Xác định màu theo score

    // Duyệt từng segment và đổi màu
    segments.forEach((segment, index) => {
        const segmentScore = index + 1; // Segment thứ n (1–10)
        if (segmentScore <= score) {
            segment.className = `rating-segment ${color}`; // Đổi màu từ trái đến điểm score
        } else {
            segment.className = 'rating-segment inactive'; // Phần còn lại giữ màu xám (inactive)
        }
    });
}

// Hàm update số điểm và text hiển thị
function updateScoreDisplay(score) {
    const scoreCircle = document.getElementById('scoreCircle'); // Vòng tròn hiển thị số
    const scoreText = document.getElementById('scoreText');     // Text mô tả điểm
    const colorClass = getScoreClass(score); // Lấy màu theo score

    scoreCircle.textContent = score; // Gán số điểm vào vòng tròn
    scoreText.textContent = getScoreDescription(score); // Lấy text từ ratingTexts

    // Xóa màu cũ
    scoreCircle.classList.remove('red', 'yellow', 'green');


    // Thêm màu mới
    if (colorClass) {
        scoreCircle.classList.add(colorClass);

    }
}

// Khi hover vào 1 segment
function handleHover(score) {
    hoveredScore = score; // Lưu điểm đang hover
    updateSegments(score, true); // Tô màu tạm
    updateScoreDisplay(score); // Update text/score tạm thời
}

// Khi rời chuột ra ngoài segment
function handleMouseLeave() {
    hoveredScore = 0; // Reset hover
    updateSegments(currentScore); // Quay về trạng thái theo điểm đã chọn
    updateScoreDisplay(currentScore);
}

// Khi click chọn điểm
function handleClick(score) {
    currentScore = score; // Ghi nhận điểm chính thức
    updateSegments(score);
    updateScoreDisplay(score);
    checkFormValidity(); // Kiểm tra form xem có bật nút post được không
}

// Hàm mở modal
function openModal() {
    document.getElementById('modalOverlay').classList.add('show'); // Hiện modal
    document.body.style.overflow = 'hidden'; // Khóa scroll trang chính
    initRatingBar(); // Tạo thanh rating mới
}

// Hàm đóng modal
function closeModal(event) {
    // Nếu bấm vào chỗ không phải overlay hoặc nút close → không đóng
    if (event && event.target !== event.currentTarget && !event.target.classList.contains('close-btn')) {
        return;
    }
    document.getElementById('modalOverlay').classList.remove('show'); // Ẩn modal
    document.body.style.overflow = 'auto'; // Cho phép scroll lại

    // Reset toàn bộ form
    currentScore = 0;
    hoveredScore = 0;
    document.getElementById('reviewText').value = ''; // Xóa text review
    updateCharacterCount(document.getElementById('reviewText')); // Cập nhật đếm ký tự
    updateScoreDisplay(0); // Reset hiển thị điểm
}

// Hàm đếm ký tự review
function updateCharacterCount(textarea) {
    const currentLength = textarea.value.length; // Số ký tự hiện tại
    const remaining = 5000 - currentLength;      // Còn lại bao nhiêu ký tự
    const minCharInfo = document.getElementById('minCharInfo'); // Thông báo yêu cầu tối thiểu
    const charCount = document.getElementById('charCount');     // Hiển thị ký tự còn lại

    charCount.textContent = remaining + ' characters remaining'; // Update text hiển thị

    // Nếu chưa đủ 75 ký tự
    if (currentLength < 75) {
        const needed = 75 - currentLength; // Còn thiếu bao nhiêu ký tự
        minCharInfo.textContent = `Minimum ${needed} characters needed`;
        minCharInfo.className = 'char-requirement needed'; // Class báo còn thiếu
    } else {
        // Nếu đủ
        minCharInfo.textContent = 'Minimum requirement met ✓';
        minCharInfo.className = 'char-requirement met'; // Class báo đã đủ
    }

    checkFormValidity(); // Kiểm tra xem nút post có bật chưa
}

// Hàm check form có hợp lệ không
function checkFormValidity() {
    const reviewText = document.getElementById('reviewText').value; // Lấy text review
    const postBtn = document.getElementById('postBtn');             // Lấy nút post

    const isValid = currentScore > 0 && reviewText.length >= 75;    // Điều kiện: có điểm và đủ 75 ký tự
    postBtn.disabled = !isValid; // Nếu không hợp lệ → disable nút
}

// Hàm submit review (gửi)
function submitReview() {
    // Chỉ gửi nếu đủ điểm và review đủ 75 ký tự
    if (currentScore > 0 && document.getElementById('reviewText').value.length >= 75) {
        alert(`Review submitted!\nScore: ${currentScore}/10 (${ratingTexts[currentScore]})\nReview: ${document.getElementById('reviewText').value.substring(0, 100)}...`);
        closeModal(); // Đóng modal sau khi gửi
    }
}

// Event: bấm phím Escape → đóng modal
document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
        closeModal();
    }
});

// Khi DOM load xong → khởi tạo thanh rating
document.addEventListener('DOMContentLoaded', function () {
    initRatingBar();
});

window.openModal = openModal;
window.closeModal = closeModal;
