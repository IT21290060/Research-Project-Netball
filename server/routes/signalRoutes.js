const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const signalController = require('../controllers/signalController');

// Set up multer storage
const storage = multer.diskStorage({
  destination: function(req, file, cb) {
    const uploadDir = path.join(__dirname, '..', 'uploads');
    
    // Create directory if it doesn't exist
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    
    cb(null, uploadDir);
  },
  filename: function(req, file, cb) {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    const ext = path.extname(file.originalname);
    cb(null, 'signal-' + uniqueSuffix + ext);
  }
});

// Create upload middleware
const upload = multer({
  storage,
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB file size limit
  fileFilter: function(req, file, cb) {
    console.log('Received file:', file.originalname);
    // Accept only images
    const filetypes = /jpeg|jpg|png|gif/;
    const mimetype = filetypes.test(file.mimetype);
    const extname = filetypes.test(path.extname(file.originalname).toLowerCase());
    
    if (mimetype && extname) {
      return cb(null, true);
    }
    
    cb(new Error('Only image files are allowed!'), false);
  }
});
 
// Routes
router.get('/', signalController.getSignals);
router.get('/:id', signalController.getSignalById);
router.post('/', upload.single('file'), signalController.createSignal);
router.post('/process', upload.single('image'), signalController.processImage);
router.delete('/:id', signalController.deleteSignal);


module.exports = router;