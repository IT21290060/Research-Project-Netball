import os
import sys
import tensorflow as tf

# Print environment information
print("Current directory:", os.getcwd())
print("Python version:", sys.version)

# Define paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
print("Script directory:", SCRIPT_DIR)

# Check netball_classifier.py
CLASSIFIER_PATH = os.path.join(SCRIPT_DIR, 'machine_learning', 'api', 'netball_classifier.py')
print(f"Checking for classifier at: {CLASSIFIER_PATH}")
print(f"File exists: {os.path.exists(CLASSIFIER_PATH)}")

# Check model directory
MODEL_DIR = os.path.join(SCRIPT_DIR, 'netball_model')
print(f"Checking for model at: {MODEL_DIR}")
print(f"Directory exists: {os.path.exists(MODEL_DIR)}")

if os.path.exists(MODEL_DIR):
    print("Model directory contents:", os.listdir(MODEL_DIR))
    
    # Try to load the model directly with TensorFlow
    try:
        model = tf.keras.models.load_model(MODEL_DIR)
        print("✅ Successfully loaded model with TensorFlow")
        print("Model summary:", model.summary())
    except Exception as e:
        print("❌ Failed to load model with TensorFlow:", str(e))

# Try to import and use NetballHandSignalClassifier
try:
    sys.path.append(os.path.join(SCRIPT_DIR, 'machine_learning', 'api'))
    from netball_classifier import NetballHandSignalClassifier
    
    print("✅ Successfully imported NetballHandSignalClassifier")
    
    # Try to create an instance
    try:
        classifier = NetballHandSignalClassifier(data_dir=None, model_path=MODEL_DIR)
        print("✅ Successfully created classifier instance")
        print("Class names:", classifier.class_names)
    except Exception as e:
        print("❌ Failed to create classifier instance:", str(e))
        
except ImportError as e:
    print("❌ Failed to import NetballHandSignalClassifier:", str(e))