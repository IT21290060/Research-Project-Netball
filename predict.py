from flask import Flask, request, jsonify
import os
import sys
import uuid
from flask_cors import CORS

# Set up correct paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"Script directory: {SCRIPT_DIR}")

# Add the machine_learning/api directory to the path
sys.path.append(os.path.join(SCRIPT_DIR, 'machine_learning', 'api'))
print(f"Python path: {sys.path}")

# Now try to import the classifier
try:
    from netball_classifier import NetballHandSignalClassifier
    print("✅ Successfully imported NetballHandSignalClassifier")
except ImportError as e:
    print(f"❌ Error importing NetballHandSignalClassifier: {e}")
    sys.exit(1)

# Flask app setup
app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

# Paths
UPLOAD_FOLDER = os.path.join(SCRIPT_DIR, 'uploads')
MODEL_DIR = os.path.join(SCRIPT_DIR, 'netball_model')

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
print(f"Upload folder: {UPLOAD_FOLDER}")
print(f"Model directory: {MODEL_DIR}")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Load classifier - explicitly pass both parameters
try:
    classifier = NetballHandSignalClassifier(data_dir=None, model_path=MODEL_DIR)
    print(f"✅ Successfully initialized classifier with model from: {MODEL_DIR}")
    print(f"Class names: {classifier.class_names}")
except Exception as e:
    print(f"❌ Error initializing classifier: {e}")
    classifier = None

def allowed_file(filename):
    """Check if the uploaded file type is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/predict', methods=['POST'])
def predict():
    """Process an uploaded image and return hand signal prediction."""
    print("📡 Received request at /predict endpoint")
    
    # Ensure classifier is loaded
    if classifier is None:
        return jsonify({'error': 'Model not initialized properly'}), 500

    # Validate file in request
    if 'file' not in request.files:
        print("⚠️ No 'file' in request")
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400

    if file and allowed_file(file.filename):
        try:
            # Generate unique filename
            unique_filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

            # Save the file
            file.save(file_path)
            print(f"✅ File saved: {file_path}")

            # Make prediction
            prediction = classifier.predict(file_path)
            print(f"🔍 Prediction result: {prediction}")

            # Format response to match what the frontend expects
            response_data = {
                'class': prediction['class'],
                'confidence': prediction['confidence'],
                'reason': prediction['feedback'],
                'above_threshold': prediction['above_threshold']
            }

            return jsonify(response_data), 200

        except Exception as e:
            print(f"❌ Error making prediction: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Error making prediction: {str(e)}'}), 500

    return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif'}), 400

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check API health status."""
    return jsonify({
        'status': 'ok',
        'model_loaded': classifier is not None,
        'upload_folder': UPLOAD_FOLDER,
        'model_directory': MODEL_DIR
    }), 200

# Start the server
if __name__ == '__main__':
    print(f"🚀 Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000)