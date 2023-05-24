from flask import Flask, render_template, send_from_directory
import os
import random
import threading
import time

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ROTATION_INTERVAL = 900  # 15 minutes in seconds

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def rotate_photos():
    while True:
        photo_files = [file for file in os.listdir(UPLOAD_FOLDER) if allowed_file(file)]
        if photo_files:
            chosen_file = random.choice(photo_files)
            filepath = os.path.join(UPLOAD_FOLDER, chosen_file)
            time.sleep(1)  # Wait for the file to be fully uploaded
            os.rename(filepath, os.path.join(UPLOAD_FOLDER, 'current_image'))
        time.sleep(ROTATION_INTERVAL)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/current_image')
def current_image():
    return send_from_directory(UPLOAD_FOLDER, 'current_image')

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    rotate_thread = threading.Thread(target=rotate_photos)
    rotate_thread.daemon = True
    rotate_thread.start()

    app.run(host='0.0.0.0', port=5000)
