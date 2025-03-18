from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import random

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes

# Create uploads folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Signal classes
CLASSES = ['start_restart', 'direction_pass', 'timeout']

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "Server is running"}), 200

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction requests"""
    print("Received prediction request")
    
    if 'file' not in request.files:
        print("No file in request")
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    # Save the file
    filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    print(f"Saved file to {filepath}")
    
    # Mock prediction result
    class_index = random.randint(0, len(CLASSES)-1)
    confidence = random.uniform(0.7, 0.95)
    
    result = {
        "class": CLASSES[class_index],
        "confidence": confidence,
        "reason": f"Mock prediction with {confidence:.2f} confidence",
        "above_threshold": True
    }
    
    print(f"Returning prediction: {result}")
    return jsonify(result), 200

@app.route('/api/signals', methods=['POST'])
def save_signal():
    """Save signal endpoint"""
    print("Received save signal request")
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    signal_type = request.form.get('signalType', '')
    accuracy = request.form.get('accuracy', 0)
    meaning = request.form.get('meaning', '')
    suggestions = request.form.get('suggestions', '')
    
    # Just mock saving to database
    return jsonify({
        "success": True,
        "message": "Signal saved successfully (mock)",
        "data": {
            "signalType": signal_type,
            "accuracy": accuracy,
            "meaning": meaning
        }
    }), 200

if __name__ == '__main__':
    print("Starting Flask server on http://localhost:5000")
    print(f"Upload folder: {os.path.abspath(UPLOAD_FOLDER)}")
    app.run(host='0.0.0.0', port=5000, debug=True)