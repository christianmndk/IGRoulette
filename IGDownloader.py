import instaloader
import os

# Create a folder to store the downloaded videos
save_folder = "static/saved_videos"
os.makedirs(save_folder, exist_ok=True)

# Initialize Instaloader
L = instaloader.Instaloader()

# Login to Instagram
USERNAME = "Username"  # Replace with your Instagram username
PASSWORD = "Password"  # Replace with your Instagram password
try:
    L.login(USERNAME, PASSWORD)
    print("Login successful!")
except instaloader.exceptions.ConnectionException as e:
    print(f"Login failed: {e}")
    exit()

# Fetch saved posts
print("Fetching saved posts...")
saved_posts = instaloader.Profile.from_username(L.context, USERNAME).get_saved_posts()

# Download only videos
for post in saved_posts:
    if post.is_video:
        video_url = post.video_url
        print(f"Downloading video: {video_url}")
        filename = os.path.join(save_folder, f"{post.mediaid}.mp4")

        # Download the video
        try:
            L.download_post(post, target=save_folder)
        except Exception as e:
            print(f"Failed to download video {post.shortcode}: {e}")

