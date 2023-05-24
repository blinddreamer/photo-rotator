from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import os
import random
import threading
import time

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png'}
IMAGE_WIDTH = 600
IMAGE_HEIGHT = 800
ROTATION_INTERVAL = 900  # 15 minutes in seconds

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image_size(image):
    width, height = image.size
    return width == IMAGE_WIDTH and height == IMAGE_HEIGHT

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

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file uploaded"

    file = request.files['file']

    if file.filename == '':
        return "No file selected"

    if file and allowed_file(file.filename):
        image = Image.open(file)
        if validate_image_size(image):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            return f"File {filename} uploaded successfully"
        else:
            return f"Invalid image dimensions. Image must be {IMAGE_WIDTH}x{IMAGE_HEIGHT} pixels."

    return "Invalid file format"

@app.route('/current_image/')
def current_image():
    photo_files = [file for file in os.listdir(UPLOAD_FOLDER) if allowed_file(file)]
    if photo_files:
        chosen_file = random.choice(photo_files)
        return send_from_directory(UPLOAD_FOLDER, chosen_file)
    else:
        return "No photo available"

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    rotate_thread = threading.Thread(target=rotate_photos)
    rotate_thread.daemon = True
    rotate_thread.start()

    app.run(host='0.0.0.0', port=5099)
