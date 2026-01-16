import cv2
import json
import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Allowed video file extensions
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

# Folder to save uploaded videos
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to get FPS using OpenCV
def get_video_fps(video_path):
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    video.release()
    return fps if fps > 0 else 30  # Default to 30 FPS if detection fails

# Function to detect "In" movements based on frame differences
def detect_in_out(video_path):
    video = cv2.VideoCapture(video_path)
    in_count = 0  # Track "In" movements
    prev_frame = None  
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = get_video_fps(video_path)
    duration = total_frames / fps  # Calculate total duration in seconds

    motion_threshold = 1000  # Minimum contour area to be considered significant motion
    prev_centroid = None
    ladder_region_y = 250  # Y-coordinate for "In" detection

    for frame_num in range(total_frames):
        ret, frame = video.read()
        if not ret:
            break

        height, width = frame.shape[:2]
        cropped_frame = frame[int(height / 2):height, 0:width]  # Focus on lower half of the frame
        gray = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if prev_frame is None:
            prev_frame = gray
            continue

        frame_diff = cv2.absdiff(prev_frame, gray)
        _, thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) > motion_threshold:
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    current_centroid = (cX, cY)

                    if prev_centroid:
                        # Check if the movement crosses the predefined ladder region
                        if prev_centroid[1] < ladder_region_y and current_centroid[1] >= ladder_region_y:
                            in_count += 1
                    prev_centroid = current_centroid
                break

        prev_frame = gray

    video.release()

    # Normalize count to a 6-second duration
    normalized_count = (in_count / duration) * 6 if duration > 0 else 0
    normalized_count = round(normalized_count, 2)

    # Calculate speed efficiency (Reps per second)
    speed_per_sec = in_count / duration if duration > 0 else 0

    # Determine efficiency rating based on speed
    if speed_per_sec >= 1.2:
        efficiency = "Excellent"
    elif 0.8 <= speed_per_sec < 1.2:
        efficiency = "Good"
    else:
        efficiency = "Needs Improvement"

    # Determine performance strength based on both normalized count & speed
    if normalized_count == 0 and speed_per_sec < 0.7:
        strength = "Low"
    if normalized_count >= 6 and speed_per_sec >= 1.0:
        strength = "High"
    elif 4 <= normalized_count < 6 and speed_per_sec >= 0.8:
        strength = "Medium"
    else:
        strength = "Low"

    return {
        "duration": round(duration, 2),
        "exercise": "InOut Ladder Drill",
        "motorskill": "Coordination",
        "count": in_count,
        "normalized_count": normalized_count,
        "speed_per_sec": round(speed_per_sec, 2),
        "efficiency": efficiency,
        "strength": strength,
        "file": ""
    }

# Endpoint to serve uploaded videos
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# API Endpoint to handle video uploads and process the In-Out drill
@app.route('/inout', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        result = detect_in_out(filepath)
        result["file"] = filename
        return jsonify(result), 200

    return jsonify({"error": "Invalid file format"}), 400

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True, port=5000)
