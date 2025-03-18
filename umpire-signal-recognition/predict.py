# from flask import Flask, request, jsonify
# import os
# import sys
# from werkzeug.utils import secure_filename
# import uuid
# from flask_cors import CORS
# import tensorflow as tf
# import numpy as np
# import json
# from tensorflow.keras.models import load_model
# from tensorflow.keras.preprocessing import image

# # Flask app setup
# app = Flask(__name__)
# # Enable CORS for all domains with more permissive settings
# CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)

# # Paths
# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# ROOT_DIR = os.path.dirname(SCRIPT_DIR)
# UPLOAD_FOLDER = os.path.join(ROOT_DIR, 'uploads')
# MODEL_DIR = os.path.join(ROOT_DIR, 'netball_model')

# # Ensure upload directory exists
# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)
#     print(f"Created upload folder: {UPLOAD_FOLDER}")
    
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# # Allowed file extensions
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# # Class names match your model's classes
# CLASS_NAMES = ['start_restart', 'direction_pass', 'timeout']

# # Initialize model
# model = None
# try:
#     model = load_model(MODEL_DIR)
#     print(f"✅ Successfully loaded model from: {MODEL_DIR}")
# except Exception as e:
#     print(f"❌ Error loading model: {e}")
#     # We'll use a mock model in this case
    
# def allowed_file(filename):
#     """Check if the uploaded file type is allowed."""
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def mock_predict_image(img_path):
#     """Mock prediction function for testing without a model"""
#     import random
#     class_idx = random.randint(0, len(CLASS_NAMES) - 1)
#     confidence = random.uniform(0.7, 0.95)
    
#     pred_class = CLASS_NAMES[class_idx]
#     feedback = f"Mock detection with {confidence:.2f} confidence. Signal is {pred_class}."
    
#     return {
#         'class': pred_class,
#         'confidence': confidence,
#         'reason': feedback,
#         'above_threshold': True
#     }

# def predict_image(img_path):
#     """
#     Predict the class of an image using the loaded model.
    
#     Args:
#         img_path (str): Path to the image file
    
#     Returns:
#         dict: Prediction results
#     """
#     try:
#         # Check if we should use the mock function
#         if model is None:
#             print("Using mock prediction as model is not loaded")
#             return mock_predict_image(img_path)
            
#         # Load and preprocess the image
#         img = image.load_img(img_path, target_size=(224, 224))
#         img_array = image.img_to_array(img)
#         img_array = np.expand_dims(img_array, axis=0)
#         img_array = img_array / 255.0  # Normalize
        
#         # Make prediction
#         prediction = model.predict(img_array)
#         class_idx = np.argmax(prediction[0])
#         confidence = float(prediction[0][class_idx])
        
#         # Threshold for valid signal
#         threshold = 0.7
#         above_threshold = confidence >= threshold
        
#         # Determine if it's a valid signal
#         if above_threshold:
#             pred_class = CLASS_NAMES[class_idx]
#             feedback = f"Detection confidence is high ({confidence:.2f}). Signal is {pred_class}."
#         else:
#             pred_class = "Not a Valid Umpire Hand Signal"
#             feedback = f"Detection confidence is low ({confidence:.2f}). Cannot reliably identify the signal."
        
#         # Create result dictionary
#         result = {
#             'class': pred_class,
#             'confidence': confidence,
#             'reason': feedback,
#             'above_threshold': above_threshold
#         }
        
#         return result
    
#     except Exception as e:
#         print(f"Error in prediction: {str(e)}")
#         return {
#             'class': 'Not a Valid Umpire Hand Signal',
#             'confidence': 0.0,
#             'reason': f'Error processing image: {str(e)}',
#             'above_threshold': False
#         }

# @app.route('/predict', methods=['POST'])
# def predict():
#     """Process an uploaded image and return hand signal prediction."""
#     print("📡 Received request at /predict endpoint")
    
#     # Validate file in request
#     if 'file' not in request.files:
#         print("⚠️ No 'file' in request")
#         return jsonify({'error': 'No image file provided'}), 400

#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'error': 'No image selected'}), 400

#     if file and allowed_file(file.filename):
#         try:
#             # Generate unique filename
#             unique_filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

#             # Save the file
#             file.save(file_path)
#             print(f"✅ File saved: {file_path}")

#             # Make prediction
#             prediction = predict_image(file_path)
#             print(f"🔍 Prediction result: {prediction}")

#             return jsonify(prediction), 200

#         except Exception as e:
#             print(f"❌ Error making prediction: {e}")
#             import traceback
#             traceback.print_exc()
#             return jsonify({'error': f'Error making prediction: {str(e)}'}), 500

#     return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif'}), 400

# # API to save signals to database (stub for now)
# @app.route('/api/signals', methods=['POST'])
# def save_signal():
#     """Save a signal to the database."""
#     try:
#         if 'file' not in request.files:
#             return jsonify({'error': 'No image file provided'}), 400
            
#         file = request.files['file']
#         signal_type = request.form.get('signalType')
#         accuracy = request.form.get('accuracy')
#         meaning = request.form.get('meaning')
#         suggestions = request.form.get('suggestions')
        
#         print(f"Received signal save request: {signal_type}, {accuracy}")
        
#         # Generate unique filename
#         unique_filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
#         file.save(file_path)
        
#         # In a real implementation, you would save to database here
#         # For now, just return success
#         return jsonify({
#             'success': True,
#             'message': 'Signal saved successfully',
#             'signal': {
#                 'imagePath': f"/uploads/{unique_filename}",
#                 'signalType': signal_type,
#                 'accuracy': float(accuracy) if accuracy else 0,
#                 'meaning': meaning,
#                 'suggestions': suggestions
#             }
#         }), 201
        
#     except Exception as e:
#         print(f"Error saving signal: {str(e)}")
#         return jsonify({'error': f'Error saving signal: {str(e)}'}), 500

# @app.route('/api/health', methods=['GET'])
# def health_check():
#     """Check API health status."""
#     return jsonify({
#         'status': 'ok',
#         'model_loaded': model is not None,
#         'upload_folder': UPLOAD_FOLDER,
#         'model_directory': MODEL_DIR
#     }), 200

# @app.route('/', methods=['GET'])
# def index():
#     """Root endpoint for basic testing"""
#     return jsonify({
#         'status': 'ok',
#         'message': 'Umpire Signal Recognition API is running'
#     }), 200

# # Ensure script only runs when executed directly
# if __name__ == '__main__':
#     print(f"🚀 Starting Flask server...")
#     print(f"Uploads saved in: {UPLOAD_FOLDER}")
#     print(f"Model directory: {MODEL_DIR}")
#     app.run(debug=True, host='0.0.0.0', port=5000)




from flask import Flask, request, jsonify
import os
import sys
from werkzeug.utils import secure_filename
import uuid
from flask_cors import CORS
import tensorflow as tf
import numpy as np
import json
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Flask app setup
app = Flask(__name__)
# Enable CORS for all domains with more permissive settings
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
UPLOAD_FOLDER = os.path.join(ROOT_DIR, 'uploads')
MODEL_DIR = os.path.join(ROOT_DIR, 'netball_model')

# Ensure upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    print(f"Created upload folder: {UPLOAD_FOLDER}")
    
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Class names match your model's classes
CLASS_NAMES = ['start_restart', 'direction_pass', 'timeout']

# Initialize model
model = None
try:
    model = load_model(MODEL_DIR)
    print(f"✅ Successfully loaded model from: {MODEL_DIR}")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    # We'll use a mock model in this case
    
def allowed_file(filename):
    """Check if the uploaded file type is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def mock_predict_image(img_path):
    """Mock prediction function for testing without a model"""
    import random
    class_idx = random.randint(0, len(CLASS_NAMES) - 1)
    confidence = random.uniform(0.7, 0.95)
    
    pred_class = CLASS_NAMES[class_idx]
    feedback = f"Mock detection with {confidence:.2f} confidence. Signal is {pred_class}."
    
    return {
        'class': pred_class,
        'confidence': confidence,
        'reason': feedback,
        'above_threshold': True
    }

def predict_image(img_path):
    """
    Predict the class of an image using the loaded model.
    
    Args:
        img_path (str): Path to the image file
    
    Returns:
        dict: Prediction results
    """
    try:
        # Check if we should use the mock function
        if model is None:
            print("Using mock prediction as model is not loaded")
            return mock_predict_image(img_path)
            
        # Load and preprocess the image
        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0  # Normalize
        
        # Make prediction
        prediction = model.predict(img_array)
        class_idx = np.argmax(prediction[0])
        confidence = float(prediction[0][class_idx])
        
        # Threshold for valid signal
        threshold = 0.7
        above_threshold = confidence >= threshold
        
        # Determine if it's a valid signal
        if above_threshold:
            pred_class = CLASS_NAMES[class_idx]
            feedback = f"Detection confidence is high ({confidence:.2f}). Signal is {pred_class}."
        else:
            pred_class = "Not a Valid Umpire Hand Signal"
            feedback = f"Detection confidence is low ({confidence:.2f}). Cannot reliably identify the signal."
        
        # Create result dictionary
        result = {
            'class': pred_class,
            'confidence': confidence,
            'reason': feedback,
            'above_threshold': above_threshold
        }
        
        return result
    
    except Exception as e:
        print(f"Error in prediction: {str(e)}")
        return {
            'class': 'Not a Valid Umpire Hand Signal',
            'confidence': 0.0,
            'reason': f'Error processing image: {str(e)}',
            'above_threshold': False
        }

@app.route('/predict', methods=['POST'])
@app.route('/api/predict', methods=['POST'])  # Add an alternative route
def predict():
    """Process an uploaded image and return hand signal prediction."""
    print("📡 Received request at /predict endpoint")
    
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
            prediction = predict_image(file_path)
            print(f"🔍 Prediction result: {prediction}")

            return jsonify(prediction), 200

        except Exception as e:
            print(f"❌ Error making prediction: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Error making prediction: {str(e)}'}), 500

    return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif'}), 400

# API to save and retrieve signals
@app.route('/api/signals', methods=['GET', 'POST'])
def handle_signals():
    """Get or save signals."""
    if request.method == 'GET':
        # Return mock signals for testing
        mock_signals = [
            {
                "_id": "1",
                "imagePath": "/uploads/sample1.jpg",
                "signalType": "start_restart",
                "accuracy": 95.4,
                "meaning": "Signal to start or restart the game",
                "createdAt": "2025-03-18T10:00:00.000Z"
            },
            {
                "_id": "2",
                "imagePath": "/uploads/sample2.jpg",
                "signalType": "timeout",
                "accuracy": 88.7,
                "meaning": "Signaling a timeout",
                "createdAt": "2025-03-17T15:30:00.000Z"
            }
        ]
        return jsonify(mock_signals), 200
    
    # POST handling for saving signals
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
            
        file = request.files['file']
        signal_type = request.form.get('signalType')
        accuracy = request.form.get('accuracy')
        meaning = request.form.get('meaning')
        suggestions = request.form.get('suggestions')
        
        print(f"Received signal save request: {signal_type}, {accuracy}")
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # In a real implementation, you would save to database here
        # For now, just return success
        return jsonify({
            'success': True,
            'message': 'Signal saved successfully',
            'signal': {
                'imagePath': f"/uploads/{unique_filename}",
                'signalType': signal_type,
                'accuracy': float(accuracy) if accuracy else 0,
                'meaning': meaning,
                'suggestions': suggestions
            }
        }), 201
        
    except Exception as e:
        print(f"Error saving signal: {str(e)}")
        return jsonify({'error': f'Error saving signal: {str(e)}'}), 500
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
            
        file = request.files['file']
        signal_type = request.form.get('signalType')
        accuracy = request.form.get('accuracy')
        meaning = request.form.get('meaning')
        suggestions = request.form.get('suggestions')
        
        print(f"Received signal save request: {signal_type}, {accuracy}")
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # In a real implementation, you would save to database here
        # For now, just return success
        return jsonify({
            'success': True,
            'message': 'Signal saved successfully',
            'signal': {
                'imagePath': f"/uploads/{unique_filename}",
                'signalType': signal_type,
                'accuracy': float(accuracy) if accuracy else 0,
                'meaning': meaning,
                'suggestions': suggestions
            }
        }), 201
        
    except Exception as e:
        print(f"Error saving signal: {str(e)}")
        return jsonify({'error': f'Error saving signal: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check API health status."""
    return jsonify({
        'status': 'ok',
        'model_loaded': model is not None,
        'upload_folder': UPLOAD_FOLDER,
        'model_directory': MODEL_DIR
    }), 200
    
@app.route('/api/signals/<signal_id>', methods=['DELETE'])
def delete_signal(signal_id):
    """Delete a signal by ID."""
    # In a real app, we would delete from database
    # For now, just return success response
    print(f"Received request to delete signal: {signal_id}")
    return jsonify({
        'success': True,
        'message': f'Signal {signal_id} deleted successfully'
    }), 200

@app.route('/', methods=['GET'])
def index():
    """Root endpoint for basic testing"""
    return jsonify({
        'status': 'ok',
        'message': 'Umpire Signal Recognition API is running'
    }), 200

# Ensure script only runs when executed directly
if __name__ == '__main__':
    print(f"🚀 Starting Flask server...")
    print(f"Uploads saved in: {UPLOAD_FOLDER}")
    print(f"Model directory: {MODEL_DIR}")
    app.run(debug=True, host='0.0.0.0', port=5000)