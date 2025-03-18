import os
import sys
import importlib.util

def check_module(module_name):
    """Check if a module can be imported"""
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            print(f"❌ Module {module_name} is NOT installed")
            return False
        else:
            print(f"✅ Module {module_name} is installed")
            return True
    except ImportError:
        print(f"❌ Error checking module {module_name}")
        return False

def check_path(path):
    """Check if a path exists"""
    if os.path.exists(path):
        print(f"✅ Path exists: {path}")
        return True
    else:
        print(f"❌ Path does NOT exist: {path}")
        return False

def main():
    """Main function to check environment"""
    print("\n=== Python Environment Check ===")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")
    
    print("\n=== Required Modules ===")
    modules = [
        "tensorflow", "numpy", "flask", "werkzeug", "uuid", 
        "flask_cors", "cv2", "matplotlib", "sklearn"
    ]
    
    for module in modules:
        check_module(module)
    
    print("\n=== Path Checks ===")
    
    # Script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    check_path(script_dir)
    
    # Check for netball_classifier.py
    parent_dir = os.path.dirname(script_dir)
    scripts_dir = os.path.join(parent_dir, "scripts")
    netball_classifier_path = os.path.join(scripts_dir, "netball_classifier.py")
    
    if check_path(scripts_dir):
        print(f"Contents of scripts directory: {os.listdir(scripts_dir)}")
    
    check_path(netball_classifier_path)
    
    # Look for netball_classifier.py in current directory
    local_classifier_path = os.path.join(script_dir, "netball_classifier.py")
    check_path(local_classifier_path)
    
    # Check for model directory
    model_dir = os.path.join(parent_dir, "netball_model")
    if check_path(model_dir):
        print(f"Contents of model directory: {os.listdir(model_dir)}")
    
    print("\n=== Import Test ===")
    try:
        sys.path.append(scripts_dir)
        import netball_classifier
        print("✅ Successfully imported netball_classifier module")
    except ImportError as e:
        print(f"❌ Failed to import netball_classifier module: {str(e)}")
        
        # Try from current directory
        try:
            sys.path.append(script_dir)
            import netball_classifier
            print("✅ Successfully imported netball_classifier module from current directory")
        except ImportError as e:
            print(f"❌ Failed to import netball_classifier module from current directory: {str(e)}")
    
    print("\n=== System Path ===")
    for i, path in enumerate(sys.path):
        print(f"{i}: {path}")
    
    print("\n=== Recommendations ===")
    print("1. Make sure the netball_classifier.py file is in the correct location")
    print("2. Ensure all required Python packages are installed")
    print("3. Check that the model files exist in the expected directory")
    print("4. Update your import statements if necessary based on your file structure")
    print("5. Run the Flask server with 'python app.py' from the directory containing app.py")

if __name__ == "__main__":
    main()