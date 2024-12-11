// Placeholder functions for queue, rate, and shadow
let videoList = []; // To store the list of visible videos
let currentVideoIndex = -1; // Tracks the index of the currently playing video

// Load the initial list of videos when the page loads
window.addEventListener('DOMContentLoaded', () => {
    const videoElements = document.querySelectorAll('.video-card img');
    videoList = Array.from(videoElements).map(img => img.dataset.video);
});
window.addEventListener('DOMContentLoaded', () => {
    const videoElements = document.querySelectorAll('.video-card img');
    videoList = Array.from(videoElements).map(img => img.getAttribute('data-video'));
});

let visitStartTime = Date.now();

window.addEventListener('beforeunload', () => {
    const visitDuration = (Date.now() - visitStartTime) / 1000; // Duration in seconds

    fetch('/log_visit_duration', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ duration: visitDuration })
    }).catch(err => console.error('Error logging visit duration:', err));
});


function logVideoView(videoFile) {
    fetch('/log_video_view', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video: videoFile })
    }).catch(err => console.error('Error logging video view:', err));
}

// Call logVideoView when a video starts playing
function showVideo(videoFile) {
    const overlay = document.getElementById('overlay');
    const overlayVideo = document.getElementById('overlay-video');

    currentVideoIndex = videoList.indexOf(videoFile);

    overlayVideo.src = `/static/saved_videos/${videoFile}`;
    overlayVideo.play(); // Auto-play the video
    logVideoView(videoFile); // Log the video view
    overlay.classList.remove('hidden');

    // Event listeners for interaction
    document.addEventListener('keydown', handleKeyDown);
    overlay.addEventListener('click', handleOverlayClick);
}

function closeOverlay() {
    const overlay = document.getElementById('overlay');
    const overlayVideo = document.getElementById('overlay-video');

    // Pause the video and clear its source to stop playback
    overlayVideo.pause();
    overlayVideo.src = '';
    overlay.classList.add('hidden');

    // Remove event listeners to clean up
    document.removeEventListener('keydown', handleKeyDown);
    overlay.removeEventListener('click', handleOverlayClick);
}

// Handle keyboard events
function handleKeyDown(event) {
    if (event.key === 'Escape') {
        closeOverlay();
    }
    if (event.key === 'ArrowRight') {
        showNextVideo();
    } else if (event.key === 'ArrowLeft') {
        showPreviousVideo();
    }
}


// Show the next video in the list
function showNextVideo() {
    if (currentVideoIndex < videoList.length - 1) {
        currentVideoIndex++;
        const nextVideo = videoList[currentVideoIndex];
        showVideo(nextVideo);
    } else {
        alert('No more videos to the right!');
    }
}

// Show the previous video in the list
function showPreviousVideo() {
    if (currentVideoIndex > 0) {
        currentVideoIndex--;
        const previousVideo = videoList[currentVideoIndex];
        showVideo(previousVideo);
    } else {
        alert('No more videos to the left!');
    }
}

// Handle overlay click
function handleOverlayClick(event) {
    const overlayContent = document.getElementById('overlay-content');
    if (!overlayContent.contains(event.target)) {
        closeOverlay();
    }
}



// Show a random video
function queueRandom() {
    if (videoList.length === 0) {
        alert('No videos available.');
        return;
    }

    // Select a random video from the list
    const randomIndex = Math.floor(Math.random() * videoList.length);
    const randomVideo = videoList[randomIndex];

    // Play the selected video in the overlay
    const overlay = document.getElementById('overlay');
    const overlayVideo = document.getElementById('overlay-video');

    overlayVideo.src = `/static/saved_videos/${randomVideo}`;
    console.log("new video playing :(", randomVideo, ")")
    overlayVideo.play(); // Auto-play the video
    overlay.classList.remove('hidden');
}
function rateVideo() {
    alert('Rate feature in progress...');
}

function shadowVideo() {
    const videoSrc = document.getElementById('overlay-video').getAttribute('src').split('/').pop();
    const pin = prompt('Enter PIN to hide this video:');

    fetch('/hide_video', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video: videoSrc, pin: pin })
    }).then(response => {
        if (response.ok) {
            alert('Video hidden successfully!');
            closeOverlay();
        } else {
            alert('Invalid PIN!');
        }
    });
}
