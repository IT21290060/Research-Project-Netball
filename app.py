import os
import random
import numpy as np
import cv2
import tensorflow as tf
import joblib

from flask import Flask, request, render_template, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from flask_cors import CORS
from tensorflow.keras.models import load_model

# === Flask Setup ===
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'your_secret_key'
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# === Model Paths ===
PASS_MODEL_PATH = 'models/netball_pass_model.h5'
SKILL_MODEL_PATH = 'models/skill_model.h5'
POSITION_MODEL_PATH = 'models/position_model.pkl'

# === Load Models ===
pass_model = tf.keras.models.load_model(PASS_MODEL_PATH) if os.path.exists(PASS_MODEL_PATH) else None
if pass_model:
    pass_model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

skill_model = load_model(SKILL_MODEL_PATH) if os.path.exists(SKILL_MODEL_PATH) else None
position_model = joblib.load(POSITION_MODEL_PATH) if os.path.exists(POSITION_MODEL_PATH) else None

position_list = [
    "Goal Attack", "Goal Keeper", "Goal Shooter", "Goal Defence",
    "Wing Attack", "Wing Defence", "Center"
]
# === Utilities ===
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_video(filepath):
    from models.pass_utils import extract_frames
    frames = extract_frames(filepath, frame_rate=1, max_frames=10, img_size=(224, 224))
    frames = np.array(frames).astype('float32') / 255.0
    return np.expand_dims(frames, axis=0)


def extract_position_frames(video_path, frame_count=30, target_size=(64, 64)):
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
    while len(frames) < frame_count:
        frames.append(np.zeros(target_size + (3,), dtype=np.float32))
    return np.array(frames).reshape(1, frame_count, *target_size, 3)

def generate_feedback(prediction):
    feedback_map = {
        "Chest Pass": [
            "Ensure proper chest-level release and follow through.",
            "Focus on your arm extension and follow-through for better accuracy.",
            "Keep the ball close to your chest for a quicker release.",
            "Make sure your hands are positioned correctly for a smooth release.",
            "Try to use your whole body for better force and control.",
            "Maintain a balanced stance and good posture during the pass.",
            "Focus on using your core for more powerful passes.",
            "Keep the ball controlled and tight to your chest before release.",
            "Practice a quick release to surprise your opponent.",
            "Watch your wrist to avoid the ball spinning unnecessarily."
        ],
        "Overhead Pass": [
            "Focus on proper hand positioning and aim for precision.",
            "Ensure your shoulders rotate fully for more power.",
            "Work on releasing the ball at a higher angle for longer passes.",
            "Maintain a steady stance while passing to avoid imbalance.",
            "Focus on keeping your arms extended to ensure a straight pass.",
            "Ensure you follow through after the release to add accuracy.",
            "Use your legs to generate additional power for the pass.",
            "Keep your eyes focused on the target to improve your aim.",
            "Make sure to release the ball smoothly from both hands.",
            "Try to release the ball higher for a more difficult-to-block pass."
        ],
        "Shoulder Pass": [
            "Improve your stance and maintain a consistent shoulder angle.",
            "Ensure your follow-through is smooth to add more control.",
            "Focus on shoulder stability and a clean release.",
            "Engage your core to add power and stability to the pass.",
            "Keep your elbow at shoulder height for maximum control.",
            "Focus on maintaining a straight line from your shoulder to your hand.",
            "Try to pass with more spin for better control over the ball.",
            "Ensure your upper body stays relaxed to avoid overcompensating.",
            "Use your whole body to generate more power for the pass.",
            "Follow through toward your target to improve accuracy."
        ],
        "Side Pass": [
            "Try to enhance the lateral movement for better accuracy.",
            "Keep the ball close to your body while passing to improve accuracy.",
            "Use your non-dominant hand to stabilize the ball for smoother passes.",
            "Work on maintaining balance during the pass for more precision.",
            "Focus on your wrist movement to add more spin and control.",
            "Ensure your shoulders and arms move fluidly for better control.",
            "Try using your legs for additional push and balance during the pass.",
            "Maintain a low body position for a more stable pass.",
            "Avoid over-extending your arm to maintain control of the ball.",
            "Ensure your non-dominant hand is actively involved in the pass."
        ],
        "Underarm Pass": [
            "Work on releasing the ball smoothly for a more effective pass.",
            "Focus on getting your elbow to extend fully during the pass.",
            "Ensure your body is aligned correctly when releasing the ball.",
            "Try to pass with a higher arc for better ball control.",
            "Work on your follow-through to increase the speed and accuracy of your passes.",
            "Make sure to keep the ball stable and low for greater precision.",
            "Focus on extending your arms fully for a smooth release.",
            "Practice releasing the ball with minimal spin for more accuracy.",
            "Ensure your feet are positioned correctly for balance during the pass.",
            "Try to aim for the chest of your teammate for a quick reception."
        ]
    }
    return random.choice(feedback_map.get(prediction, ["Good job! Keep practicing."]))


# === Routes ===
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/pass', methods=['GET', 'POST'])
def recognize_pass():
    if request.method == 'POST':
        video = request.files.get('video')
        if not video or video.filename == '':
            flash('No video file uploaded.')
            return redirect(request.url)
        if not allowed_file(video.filename):
            flash('Invalid file type.')
            return redirect(request.url)

        filename = secure_filename(video.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        video.save(filepath)

        if not pass_model:
            flash('Pass recognition model not loaded.')
            return redirect(request.url)

        try:
            video_frames = preprocess_video(filepath)
            prediction_probs = pass_model.predict(video_frames)
            prediction_class = tf.argmax(prediction_probs, axis=1).numpy()[0]

            class_mapping = {
                0: "Chest Pass",
                1: "Overhead Pass",
                2: "Shoulder Pass",
                3: "Side Pass",
                4: "Underarm Pass"
            }

            prediction = class_mapping.get(prediction_class, "Unknown")
            probability = round(float(prediction_probs[0][prediction_class]) * 100, 2)
            feedback = generate_feedback(prediction)

            return redirect(url_for('result_pass', prediction=prediction, probability=probability, feedback=feedback))

        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    return render_template('upload_pass.html')
@app.route('/position', methods=['GET', 'POST'])
def recognize_position():
    if request.method == 'POST':
        video = request.files.get('file')
        if not video or video.filename == '':
            flash('No video file uploaded.')
            return redirect(request.url)
        if not allowed_file(video.filename):
            flash('Invalid file type.')
            return redirect(request.url)

        filename = secure_filename(video.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        video.save(filepath)

        frames = extract_position_frames(filepath)
        os.remove(filepath)

        skills = []
        position = "Unknown"
        playing_area_image = ''

        if skill_model and position_model:
            skill_probs = skill_model.predict(np.array(frames))[0]

            skills = [
                {'name': name, 'value': round(float(prob) * 100, 1)}
                for name, prob in zip(
                    ['Attacking', 'Ball Handling', 'Defending', 'Footwork', 'Shooting'],
                    skill_probs
                )
            ]

            predicted_index = position_model.predict(skill_probs.reshape(1, -1))[0]
            position = position_list[predicted_index]

            position_images = {
                "Goal Attack": "goal_attack.jpg",
                "Goal Keeper": "goal_keeper.jpg",
                "Goal Shooter": "goal_shooter.jpg",
                "Goal Defence": "goal_defence.jpg",
                "Wing Attack": "wing_attack.jpg",
                "Wing Defence": "wing_defence.jpg",
                "Center": "center.jpg"
            }

            playing_area_image = position_images.get(position, '')

        # Store results in session
        session['skills'] = skills
        session['position'] = position
        session['playing_area_image'] = playing_area_image

        return redirect(url_for('result_position'))

    return render_template('upload_position.html')
@app.route('/result_pass')
def result_pass():
    prediction = request.args.get('prediction', 'Unknown')
    probability = request.args.get('probability', '0.00')
    feedback = request.args.get('feedback', 'No feedback available')

    return render_template(
        'result_pass.html',
        prediction=prediction,
        probability=probability,
        feedback=feedback
    )

@app.route('/result_position')
def result_position():
    skills = session.get('skills', [])
    position = session.get('position', 'Unknown')
    playing_area_image = session.get('playing_area_image', '')

    # ✅ Add this line:
    position_logo = position.lower().replace(" ", "_") + "_logo.jpg"

    return render_template(
        'result_position.html',
        skills=skills,
        position=position,
        playing_area_image=playing_area_image,
        position_logo=position_logo  # ✅ Pass it to the template
    )


# === Run App ===
if __name__ == '__main__':
    app.run(debug=True)
