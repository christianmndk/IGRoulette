#from flask import Flask, render_template, request, redirect, make_response, jsonify, session
from flask import Flask, render_template, request, redirect, url_for, session, make_response, jsonify
import uuid
import time
import os

app = Flask(__name__)

def get_or_set_visitor_id():
    visitor_id = request.cookies.get('visitor_id')
    if not visitor_id:
        visitor_id = str(uuid.uuid4())  # Generate a new unique ID
    return visitor_id

def log_visit(visitor_id):
    with open('visit_log.txt', 'a') as log_file:
        log_file.write(f"{visitor_id},{time.time()}\n")

app.secret_key = 'latex'  # Replace with a strong secret key


@app.route('/')
def index():
    # Get or set a unique visitor ID
    visitor_id = get_or_set_visitor_id()

    # Log the visit
    log_visit(visitor_id)

    # Load the video gallery
    saved_videos_path = 'static/saved_videos'
    hidden_videos_file = 'hidden_videos.txt'

    # Load hidden video filenames
    hidden_videos = set()
    if os.path.exists(hidden_videos_file):
        with open(hidden_videos_file, 'r') as file:
            hidden_videos = set(line.strip() for line in file)

    # List all thumbnails and match them with their videos
    thumbnails = [
        f for f in os.listdir(saved_videos_path) if f.endswith('.jpg')
    ]
    videos = {
        thumb: thumb.replace('.jpg', '.mp4')
        for thumb in thumbnails
        if os.path.exists(os.path.join(saved_videos_path, thumb.replace('.jpg', '.mp4')))
    }

    # Filter out hidden videos
    visible_videos = {
        thumb: video for thumb, video in videos.items() if video not in hidden_videos
    }

    # Create response and set the cookie
    response = make_response(render_template('index.html', videos=visible_videos))
    response.set_cookie('visitor_id', visitor_id, max_age=60*60*24*365)  # 1-year cookie

    return response



@app.route('/hide_video', methods=['POST'])
def hide_video():
    # Path to hidden videos list
    hidden_videos_file = 'hidden_videos.txt'

    # Get video filename and PIN from the request
    video = request.json.get('video')
    pin = request.json.get('pin')

    # Check the PIN (example PIN is '1234')
    if pin == "1234":
        # Write the video filename to hidden_videos.txt
        with open(hidden_videos_file, 'a') as file:
            file.write(video + '\n')
        return jsonify({"status": "success"}), 200

    return jsonify({"status": "error", "message": "Invalid PIN"}), 401


@app.route('/log_video_view', methods=['POST'])
def log_video_view():
    visitor_id = request.cookies.get('visitor_id')
    video = request.json.get('video')
    timestamp = time.time()

    if visitor_id and video:
        with open('video_views_log.txt', 'a') as log_file:
            log_file.write(f"{visitor_id},{video},{timestamp}\n")
        return jsonify({"status": "success"}), 200

    return jsonify({"status": "error"}), 400


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # Admin login
    if session.get('admin'):
        return redirect(url_for('admin_panel'))

    if request.method == 'POST':
        pin = request.form.get('pin')
        if pin == "1205":  # Example PIN
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            return render_template('admin.html', error="Invalid PIN")

    return render_template('admin.html')


@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin'))

    # Total videos
    video_count = len([f for f in os.listdir('static/saved_videos') if f.endswith('.mp4')])

    # Hidden videos
    hidden_video_count = 0
    if os.path.exists('hidden_videos.txt'):
        with open('hidden_videos.txt', 'r') as file:
            hidden_video_count = len(file.readlines())

    # Unique visitors
    unique_visitors = set()
    admin_id = request.cookies.get('visitor_id')  # Get the current visitor ID
    if os.path.exists('visit_log.txt'):
        with open('visit_log.txt', 'r') as file:
            unique_visitors = {line.split(',')[0] for line in file.readlines()}

    # Add (admin) tag to the admin's identifier
    unique_visitors_list = [
        f"{user} (admin)" if user == admin_id else user for user in unique_visitors
    ]

    stats = {
        'total_videos': video_count,
        'hidden_videos': hidden_video_count,
        'unique_visitors_count': len(unique_visitors),
        'unique_visitors_list': unique_visitors_list
    }

    return render_template('admin_panel.html', stats=stats)




@app.route('/admin/manage_hidden', methods=['GET', 'POST'])
def manage_hidden():
    if not session.get('admin'):
        return redirect(url_for('admin'))

    hidden_videos = []
    if os.path.exists('hidden_videos.txt'):
        with open('hidden_videos.txt', 'r') as file:
            hidden_videos = [line.strip() for line in file]

    if request.method == 'POST':
        video_to_restore = request.form.get('restore_video')
        hidden_videos = [
            video for video in hidden_videos if video != video_to_restore
        ]
        with open('hidden_videos.txt', 'w') as file:
            for video in hidden_videos:
                file.write(video + '\n')
        return redirect(url_for('manage_hidden'))

    return render_template('manage_hidden.html', hidden_videos=hidden_videos)


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(debug=True)
