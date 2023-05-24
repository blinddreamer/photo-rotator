from flask import Flask, render_template, request, send_from_directory, make_response
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

current_image_filename = None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image_size(image):
    width, height = image.size
    return width == IMAGE_WIDTH and height == IMAGE_HEIGHT

def rotate_photos():
    rotate_interval = 0  # Start rotating immediately upon starting the application
    while True:
        photo_files = [file for file in os.listdir(UPLOAD_FOLDER) if allowed_file(file)]
        if photo_files:
            global current_image_filename

            # Select a new random image
            chosen_file = random.choice(photo_files)
            filepath = os.path.join(UPLOAD_FOLDER, chosen_file)

            # Rename the new image to current_image.png
            os.replace(filepath, os.path.join(UPLOAD_FOLDER, 'current_image.png'))
            current_image_filename = 'current_image.png'

        time.sleep(rotate_interval)
        rotate_interval = ROTATION_INTERVAL  # Set the rotation interval for subsequent rotations

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

@app.route('/current_image.png')
def get_current_image():
    global current_image_filename

    if current_image_filename:
        return send_from_directory(UPLOAD_FOLDER, current_image_filename)
    else:
        return "No photo available"

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    rotate_thread = threading.Thread(target=rotate_photos)
    rotate_thread.daemon = True
    rotate_thread.start()

    app.run(host='0.0.0.0', port=5099)
