import os
import random
import time
from flask import Flask, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png'}
IMAGE_WIDTH = 600
IMAGE_HEIGHT = 800
PHOTO_CHANGE_INTERVAL = 15 * 60  # 15 minutes (in seconds)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

last_photo_update_time = 0
current_photo = None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_random_photo():
    global last_photo_update_time, current_photo

    current_time = time.time()
    if current_photo is None or current_time - last_photo_update_time >= PHOTO_CHANGE_INTERVAL:
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        image_files = [file for file in files if allowed_file(file)]
        if image_files:
            current_photo = random.choice(image_files)
            last_photo_update_time = current_time

    return current_photo

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return redirect(url_for('uploaded_file', filename=filename))
    return '''
    <!doctype html>
    <html>
    <head>
    <title>Image Uploader</title>
    </head>
    <body>
    <h1>Upload an Image</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    </body>
    </html>
    '''

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/random_photo')
def random_photo():
    photo = get_random_photo()
    if photo:
        return send_from_directory(app.config['UPLOAD_FOLDER'], photo)
    return 'No images uploaded yet.'

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host='0.0.0.0', port=3000)
