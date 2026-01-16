import os
import numpy as np
import tensorflow as tf
from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
import cv2
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Define constants
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}
FRAME_SIZE = (128, 128)
SEQ_LENGTH = 30
CLASSES = ['360_rotation', 'In_out', 'Squat', 'T_run', 'X_drill', 'Zig_zag']

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Load the trained model
model = load_model('exercise_classification_model.keras')

# Helper function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Preprocess video data
def preprocess_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, FRAME_SIZE)
        frames.append(frame)
    cap.release()
    frames = np.array(frames)
    # Select SEQ_LENGTH evenly spaced frames
    if len(frames) >= SEQ_LENGTH:
        indices = np.linspace(0, len(frames) - 1, SEQ_LENGTH).astype(int)
        frames = frames[indices]
    else:
        # Pad with black frames if video is shorter
        pad_len = SEQ_LENGTH - len(frames)
        frames = np.pad(frames, ((0, pad_len), (0, 0), (0, 0), (0, 0)), mode='constant')
    return frames / 255.0  # Normalize

@app.route('/predict', methods=['POST'])
def predict():
    # Check if the request contains a file
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']

    # Check if the file is valid
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    # Save the file to the upload folder
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        # Preprocess the video
        video_data = preprocess_video(file_path)
        video_data = np.expand_dims(video_data, axis=0)  # Add batch dimension

        # Predict using the model
        predictions = model.predict(video_data)
        class_index = np.argmax(predictions)
        confidence = predictions[0][class_index]

        # Get the class name
        exercise_name = CLASSES[class_index]

        # Return the result
        result = {
            'exercise': exercise_name,
            'confidence': float(confidence)
        }
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        # Clean up the uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True,port=5004)
