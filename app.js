const express = require('express');
const multer = require('multer');
const sharp = require('sharp');
const fs = require('fs');
const path = require('path');
import random from 'random';

const app = express();
const upload = multer({ dest: 'uploads/' });
const PORT = 5099;

const UPLOAD_FOLDER = 'uploads';
const ALLOWED_EXTENSIONS = ['png'];
const IMAGE_WIDTH = 600;
const IMAGE_HEIGHT = 800;
const ROTATION_INTERVAL = 900; // 15 minutes in seconds

let currentImageFilename = null;

const allowedFile = (filename) => {
  const ext = path.extname(filename).toLowerCase();
  return ALLOWED_EXTENSIONS.includes(ext);
};

const validateImageSize = async (file) => {
  const image = await sharp(file.path).metadata();
  return image.width === IMAGE_WIDTH && image.height === IMAGE_HEIGHT;
};

const rotatePhotos = () => {
  let rotateInterval = 0; // Start rotating immediately upon starting the application
  setInterval(() => {
    const photoFiles = fs.readdirSync(UPLOAD_FOLDER).filter(allowedFile);
    if (photoFiles.length > 0) {
      currentImageFilename = random.pick(photoFiles);
      fs.renameSync(
        path.join(UPLOAD_FOLDER, currentImageFilename),
        path.join(UPLOAD_FOLDER, 'current_image.png')
      );
    }
    rotateInterval = ROTATION_INTERVAL; // Set the rotation interval for subsequent rotations
  }, rotateInterval * 1000);
};

app.get('/', (req, res) => {
  res.send('Hello, world!');
});

app.post('/upload', upload.single('file'), async (req, res) => {
  if (!req.file) {
    return res.status(400).send('No file uploaded');
  }

  if (!(await validateImageSize(req.file))) {
    return res.status(400).send(`Invalid image dimensions. Image must be ${IMAGE_WIDTH}x${IMAGE_HEIGHT} pixels.`);
  }

  return res.send(`File ${req.file.filename} uploaded successfully`);
});

app.get('/current_image.png', (req, res) => {
  if (currentImageFilename) {
    const imageStream = fs.createReadStream(path.join(UPLOAD_FOLDER, 'current_image.png'));
    res.setHeader('Content-Type', 'image/png');
    imageStream.pipe(res);
  } else {
    res.status(404).send('No photo available');
  }
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  if (!fs.existsSync(UPLOAD_FOLDER)) {
    fs.mkdirSync(UPLOAD_FOLDER);
  }
  rotatePhotos();
});
