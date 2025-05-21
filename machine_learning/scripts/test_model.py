import os
import sys
import argparse
import json
import numpy as np
import matplotlib.pyplot as plt
import cv2

# Add parent directory to path to import netball_classifier
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from netball_classifier import NetballHandSignalClassifier

def display_prediction(image_path, prediction):
    """
    Display the image with prediction results.
    
    Args:
        image_path (str): Path to the image
        prediction (dict): Prediction results
    """
    # Read image
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Get prediction info
    pred_class = prediction['class']
    confidence = prediction['confidence']
    feedback = prediction['feedback']
    
    # Create figure
    plt.figure(figsize=(10, 8))
    
    # Display image
    plt.imshow(img)
    
    # Create title with prediction info
    title = f"Prediction: {pred_class}\nConfidence: {confidence:.2f}"
    plt.title(title)
    
    # Add feedback as text at the bottom
    plt.figtext(0.5, 0.01, feedback, wrap=True, horizontalalignment='center', fontsize=12)
    
    # Remove axis
    plt.axis('off')
    
    # Save plot
    result_path = os.path.splitext(image_path)[0] + "_prediction.png"
    plt.savefig(result_path, bbox_inches='tight')
    plt.close()
    
    print(f"Prediction visualization saved to: {result_path}")
    
    return result_path

def main():
    """
    Main function to test the netball hand signal classifier.
    """
    parser = argparse.ArgumentParser(description='Test netball hand signal classifier')
    
    # Add arguments
    parser.add_argument('--model_path', type=str, required=True,
                        help='Path to the saved model')
    parser.add_argument('--test_image', type=str, required=True,
                        help='Path to the test image')
    parser.add_argument('--threshold', type=float, default=0.7,
                        help='Confidence threshold for predictions')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check if model directory exists
    if not os.path.exists(args.model_path):
        print(f"Error: Model directory '{args.model_path}' does not exist.")
        return
    
    # Check if test image exists
    if not os.path.exists(args.test_image):
        print(f"Error: Test image '{args.test_image}' does not exist.")
        return
    
    # Initialize the classifier
    classifier = NetballHandSignalClassifier(
        data_dir=None,  # Not needed for prediction
        model_path=args.model_path
    )
    
    # Make prediction
    print(f"Making prediction for image: {args.test_image}")
    prediction = classifier.predict(args.test_image, threshold=args.threshold)
    
    # Print prediction
    print("\n=== Prediction Results ===")
    print(f"Predicted class: {prediction['class']}")
    print(f"Confidence: {prediction['confidence']:.4f}")
    print(f"Above threshold: {prediction['above_threshold']}")
    print(f"Feedback: {prediction['feedback']}")
    print("\nClass probabilities:")
    for class_name, prob in prediction['all_probabilities'].items():
        print(f"  {class_name}: {prob:.4f}")
    print("========================")
    
    # Display prediction
    display_prediction(args.test_image, prediction)

if __name__ == "__main__":
    main()