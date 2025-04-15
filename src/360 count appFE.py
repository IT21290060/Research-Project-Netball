import cv2
import mediapipe as mp
import numpy as np
import time
from flask import Flask, request, jsonify, send_from_directory
import os
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize MediaPipe pose solution
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Function to calculate angle between 3 points
def calculate_angle(a, b, c):
    a = np.array(a)  # First point
    b = np.array(b)  # Midpoint
    c = np.array(c)  # End point

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

# Function to check rotation and count 360-degree jumps
def count_jumps(landmarks, count, in_rotation, prev_angle):
    left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
    right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
    left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
    right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
    
    torso_angle = calculate_angle(left_hip, left_shoulder, right_shoulder)

    # We are tracking the rate of change of angle to catch fast rotations
    angle_change = abs(torso_angle - prev_angle)

    if angle_change > 30 and not in_rotation:  # If the change in angle is significant, start counting a rotation
        in_rotation = True
    elif angle_change < 15 and in_rotation:  # If the angle change slows down, consider it a completed rotation
        count += 1
        in_rotation = False

    return count, in_rotation, torso_angle

# Function to determine strength level based on count in 10 seconds
def determine_strength(count, duration):
    # Normalize count to a 10-second interval
    normalized_count_per_10_sec = (count / duration) * 10

    # Based on the normalized counts per 10 seconds
    if normalized_count_per_10_sec >= 6.67:  # More than or equal to 4 counts in 6 seconds = High
        return "High"
    elif normalized_count_per_10_sec >= 5:  # More than or equal to 4 counts in 8 seconds = Medium
        return "Medium"
    else:  # Less than 4 counts in 10 seconds = Low
        return "Low"

# API endpoint for video upload and processing
@app.route('/process_video', methods=['POST'])
def process_video():
    # Get video file from POST request
    video_file = request.files.get('file')

    if not video_file:
        return jsonify({'error': 'No video file uploaded'}), 400

    # Ensure 'uploads' directory exists
    upload_folder = 'uploads'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Save the video file to the 'uploads' directory
    video_path = os.path.join(upload_folder, video_file.filename)
    video_file.save(video_path)

    # Open video with OpenCV
    cap = cv2.VideoCapture(video_path)

    # Get video metadata for accurate duration
    fps = cap.get(cv2.CAP_PROP_FPS)  # Frames per second
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # Total frames
    actual_duration = total_frames / fps if fps > 0 else 0  # Compute real duration

    # Variables to store jump count, rotation state, and previous angle
    count = 0
    in_rotation = False
    prev_angle = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the frame color to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame for pose detection
        results = pose.process(image)

        # Convert the frame color back to BGR for OpenCV
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            # Extract landmark points
            landmarks = results.pose_landmarks.landmark

            # Count 360-degree jumps
            count, in_rotation, prev_angle = count_jumps(landmarks, count, in_rotation, prev_angle)

    cap.release()

    # Determine motor skill level (based on normalized count per 10 seconds)
    motorskill = determine_strength(count, actual_duration)

    # Return the results in the expected format
    return jsonify({
        'duration': round(actual_duration, 2),  # Accurate duration from metadata
        'exercise': 'Balance',
        'motorskill': motorskill,
        'file': video_file.filename,        
        'count': count,
        'strength': motorskill,
        'timer': round(actual_duration, 2)  # Consistent with duration
    })

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

if __name__ == '__main__':
    app.run(debug=True, port=5002)
