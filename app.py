from flask import Flask, render_template, request, send_from_directory
from PIL import Image
import os
import threading
import time

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
IMAGE_WIDTH = 600
IMAGE_HEIGHT = 800

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image_size(image):
    width, height = image.size
    return width == IMAGE_WIDTH and height == IMAGE_HEIGHT

def rotate_photos():
    while True:
        for filename in os.listdir(UPLOAD_FOLDER):
            if allowed_file(filename):
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                image = Image.open(filepath)
                if validate_image_size(image):
                    rotated_image = image.rotate(90)  # Rotate the image by 90 degrees
                    rotated_image.save(filepath)
        time.sleep(900)  # Sleep for 15 minutes (900 seconds)

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
            filename = file.filename
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            return f"File {filename} uploaded successfully"
        else:
            return f"Invalid image dimensions. Image must be {IMAGE_WIDTH}x{IMAGE_HEIGHT} pixels."

    return "Invalid file format"

@app.route('/photos/<filename>')
def photos(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    rotate_thread = threading.Thread(target=rotate_photos)
    rotate_thread.daemon = True
    rotate_thread.start()

    app.run(host='0.0.0.0', port=80)