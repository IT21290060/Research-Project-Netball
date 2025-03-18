import os
import sys

# Add parent directory to path to import netball_classifier
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Current directory:", os.getcwd())
print("Python path:", sys.path)

try:
    # Try importing the classifier
    from netball_classifier import NetballHandSignalClassifier
    print("✅ Successfully imported NetballHandSignalClassifier")
    
    # Locate model directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    model_dir = os.path.join(root_dir, 'netball_model')
    
    print(f"Looking for model in: {model_dir}")
    
    if os.path.exists(model_dir):
        print(f"✅ Model directory exists: {model_dir}")
        print(f"Contents: {os.listdir(model_dir)}")
        
        # Try loading the model
        try:
            classifier = NetballHandSignalClassifier(data_dir=None, model_path=model_dir)
            print("✅ Successfully loaded model")
            
            # Check if class_names are loaded
            if classifier.class_names:
                print(f"✅ Class names: {classifier.class_names}")
            else:
                print("❌ No class names loaded")
                
        except Exception as e:
            print(f"❌ Error loading model: {e}")
    else:
        print(f"❌ Model directory not found: {model_dir}")
        
except ImportError as e:
    print(f"❌ Error importing NetballHandSignalClassifier: {e}")
    print("Make sure the file is in the correct location.")

print("\nRecommendations:")
print("1. Ensure netball_classifier.py is in the correct directory")
print("2. Check that the model directory exists and contains saved_model.pb and other files")
print("3. Verify that class_names.json exists in the model directory")