import os
from flask import Flask, request, jsonify, send_from_directory
import numpy as np
import cv2
import mediapipe as mp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Ensure the temp directory exists
if not os.path.exists('temp'):
    os.makedirs('temp')

# Function to calculate angle between three points
def calculate_angle(a, b, c):
    a = np.array(a)  # First point
    b = np.array(b)  # Midpoint
    c = np.array(c)  # Last point
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians) * 180.0 / np.pi
    if angle > 180.0:
        angle = 360 - angle
    return angle

# Analyze the squat video
def analyze_squat_video(video_path):
    squat_count = 0
    duration = 0

    cap = cv2.VideoCapture(video_path)
    squat_in_progress = False  # Track squat cycle
    fps = cap.get(cv2.CAP_PROP_FPS) or 30  # Handle cases where FPS is not available
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
        
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP].y]
            knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y]
            ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y]
            
            knee_angle = calculate_angle(hip, knee, ankle)
            
            if knee_angle < 90 and not squat_in_progress:
                squat_in_progress = True
            elif knee_angle > 160 and squat_in_progress:
                squat_count += 1
                squat_in_progress = False
        
    duration = frame_count / fps  # Calculate duration in seconds
    cap.release()
    cv2.destroyAllWindows()
    
    # Determine performance based on count and duration
    if squat_count < 3 and duration <= 10:
        strength = "Low"
    elif 7 <= squat_count < 10 and duration <= 10:
        strength = "Medium"
    elif squat_count >= 10 and duration <= 10:
        strength = "High"
    else:
        strength = "Medium"  # Default if outside conditions

    return squat_count, strength, duration

@app.route('/analyze_video', methods=['POST'])
def analyze_video():
    if 'file' not in request.files:
        return jsonify({'error': 'No video file found'}), 400
    
    video_file = request.files['file']
    video_path = os.path.join('temp', video_file.filename)
    video_file.save(video_path)

    squat_count, strength, duration = analyze_squat_video(video_path)
    
    print(f"Squat Count: {squat_count}, Strength: {strength}, Duration: {duration}")
    
    return jsonify({
        'motorskill': "Squats",
        'exercise': "Power",
        'count': int(squat_count),
        'strength': strength,
        'duration': float(duration),
        'file': video_file.filename
    })

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('temp', filename)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
