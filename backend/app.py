from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
import os
import numpy as np
import cv2
import joblib
from tensorflow.keras.models import load_model

app = Flask(__name__, template_folder='../templates', static_folder='../static')
CORS(app)
app.secret_key = 'your_secret_key'  

# Paths to models
SKILL_MODEL_PATH = 'models/skill_model.h5'
POSITION_MODEL_PATH = 'models/position_model.pkl'
UPLOAD_FOLDER = 'uploads/'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Verify models exist
if not os.path.exists(SKILL_MODEL_PATH) or not os.path.exists(POSITION_MODEL_PATH):
    raise FileNotFoundError("Missing model files")

# Load models
skill_model = load_model(SKILL_MODEL_PATH)
position_model = joblib.load(POSITION_MODEL_PATH)

position_list = [
    "Goal Attack", "Goal Keeper", "Goal Shooter", "Goal Defence",
    "Wing Attack", "Wing Defence", "Center"
]

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/upload')
def upload():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    video_file = request.files['file']
    if video_file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    # Process video
    video_id = save_uploaded_video(video_file)
    frames = extract_frames(os.path.join(UPLOAD_FOLDER, video_id))

    # Get skill predictions
    skill_probs = skill_model.predict(np.array(frames))[0]
    skills = [
        {'name': name, 'value': round(float(prob) * 100, 1)}
        for name, prob in zip(
            ['Attacking', 'Ball Handling', 'Defending', 'Footwork', 'Shooting'],
            skill_probs
        )
    ]

    # Get position prediction
    skill_probs_scaled = skill_probs.reshape(1, -1)
    predicted_position_index = position_model.predict(skill_probs_scaled)[0]
    predicted_position = position_list[predicted_position_index]

    # Store results in session
    session['skills'] = skills
    session['position'] = predicted_position
    session['video_id'] = video_id

    # Redirect to result page
    return redirect(url_for('result'))

@app.route('/result')
def result():
    # Retrieve results from session
    skills = session.get('skills', [])
    position = session.get('position', 'Unknown')
    video_id = session.get('video_id', '')

    # Map position to playing area image filename
    position_images = {
        "Goal Attack": "goal_attack.jpg",
        "Goal Keeper": "goal_keeper.jpg",
        "Goal Shooter": "goal_shooter.jpg",
        "Goal Defence": "goal_defence.jpg",
        "Wing Attack": "wing_attack.jpg",
        "Wing Defence": "wing_defence.jpg",
        "Center": "center.jpg"
    }

    # Get the playing area image filename
    playing_area_image = position_images.get(position, '')

    return render_template('result.html', skills=skills, position=position, playing_area_image=playing_area_image)

def save_uploaded_video(video_file):
    extension = os.path.splitext(video_file.filename)[1]
    video_id = f"video_{np.random.randint(100000, 999999)}{extension}"
    video_file.save(os.path.join(UPLOAD_FOLDER, video_id))
    return video_id

def extract_frames(video_path, frame_count=30, target_size=(64, 64)):
    cap = cv2.VideoCapture(video_path)
    frames = []

    while len(frames) < frame_count:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, target_size)
        frame = frame.astype('float32') / 255.0
        frames.append(frame)

    cap.release()

    # Pad with black frames if needed
    while len(frames) < frame_count:
        frames.append(np.zeros(target_size + (3,), dtype=np.float32))

    return np.array(frames).reshape(1, frame_count, *target_size, 3)

if __name__ == '__main__':
    app.run(debug=True)