let player;
let watchStartTime = null;      // thời điểm bắt đầu PLAY
let totalWatchTime = 0;         // tổng thời gian đã xem
let isPlaying = false;
let videoEnded = false;         // đánh dấu video đã END chưa

document.addEventListener('DOMContentLoaded', function () {
    const movieId = extractMovieIdFromURL();

    // ✅ Nếu người dùng đổi trang giữa chừng
    window.addEventListener('beforeunload', function () {
        if (!movieId) return;

        // Nếu đang play → cộng nốt thời gian
        if (isPlaying && watchStartTime) {
            totalWatchTime += Math.floor((Date.now() - watchStartTime) / 1000);
            isPlaying = false;
        }

        // Nếu video chưa kết thúc → gửi log "left_page"
        if (!videoEnded && totalWatchTime > 0) {
            logUserEvent({
                action_type: "trailer",
                event: "left_page",
                movie_id: movieId,
                trailer_time: totalWatchTime,
                timestamp: new Date().toISOString(),
                user_agent: navigator.userAgent
            });
        }
    });
});

// ✅ YouTube API ready
function onYouTubeIframeAPIReady() {
    console.log("✅ YouTube API ready.");
}

// ✅ Lắng nghe trạng thái player
function onPlayerStateChange(event) {
    const movieId = extractMovieIdFromURL();
    if (!movieId) return;

    const state = event.data;

    if (state === YT.PlayerState.PLAYING) {
        // Bắt đầu ghi nhận thời gian xem
        if (!isPlaying) {
            watchStartTime = Date.now();
            isPlaying = true;
        }
    }

    if (state === YT.PlayerState.PAUSED && isPlaying) {
        // Cộng dồn thời gian khi pause
        totalWatchTime += Math.floor((Date.now() - watchStartTime) / 1000);
        isPlaying = false;
    }

    if (state === YT.PlayerState.ENDED) {
        // Khi video xem xong
        if (isPlaying) {
            totalWatchTime += Math.floor((Date.now() - watchStartTime) / 1000);
            isPlaying = false;
        }

        videoEnded = true; // đánh dấu video đã END

        // ✅ Gửi log duy nhất khi video kết thúc
        logUserEvent({
            action_type: "trailer",
            event: "finished",
            movie_id: movieId,
            trailer_time: totalWatchTime,
            timestamp: new Date().toISOString(),
            user_agent: navigator.userAgent
        });

        // Reset cho lượt xem lại sau
        totalWatchTime = 0;
    }
}

// ✅ Hàm gửi log về backend
function logUserEvent(logData) {
    fetch('http://127.0.0.1:5000/api/v1/log/user_event', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(logData)
    }).catch(console.warn);
}

// ✅ Lấy movie_id từ URL
function extractMovieIdFromURL() {
    const url = new URL(window.location.href);
    const id = url.searchParams.get("movie_id");
    return id ? parseInt(id) : null;
}
