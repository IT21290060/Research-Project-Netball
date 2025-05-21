import os
import argparse
from netball_classifier import NetballHandSignalClassifier

def main():
    """
    Main function to train and evaluate the netball hand signal classifier.
    """
    parser = argparse.ArgumentParser(description='Train netball hand signal classifier')
    
    # Add arguments
    parser.add_argument('--data_dir', type=str, default='data',
                        help='Directory containing the dataset')
    parser.add_argument('--img_height', type=int, default=224,
                        help='Image height for resizing')
    parser.add_argument('--img_width', type=int, default=224,
                        help='Image width for resizing')
    parser.add_argument('--batch_size', type=int, default=32,
                        help='Batch size for training')
    parser.add_argument('--val_split', type=float, default=0.2,
                        help='Fraction of data to use for validation')
    parser.add_argument('--epochs', type=int, default=30,
                        help='Number of epochs to train')
    parser.add_argument('--fine_tune_at', type=int, default=10,
                        help='Epoch to start fine-tuning from')
    parser.add_argument('--model_path', type=str, default='netball_model',
                        help='Path to save the trained model')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check if data directory exists
    if not os.path.exists(args.data_dir):
        print(f"Error: Data directory '{args.data_dir}' does not exist.")
        return
    
    # Print training settings
    print("=== Training Settings ===")
    print(f"Data directory: {args.data_dir}")
    print(f"Image dimensions: {args.img_height}x{args.img_width}")
    print(f"Batch size: {args.batch_size}")
    print(f"Validation split: {args.val_split}")
    print(f"Epochs: {args.epochs}")
    print(f"Fine-tuning at epoch: {args.fine_tune_at}")
    print(f"Model save path: {args.model_path}")
    print("========================")
    
    # Initialize the classifier
    classifier = NetballHandSignalClassifier(
        data_dir=args.data_dir,
        img_height=args.img_height,
        img_width=args.img_width,
        batch_size=args.batch_size
    )
    
    # Print dataset statistics
    print("\n=== Dataset Analysis ===")
    # Count images in each class
    class_counts = {}
    for class_name in os.listdir(args.data_dir):
        class_path = os.path.join(args.data_dir, class_name)
        if os.path.isdir(class_path):
            file_count = len([f for f in os.listdir(class_path) if os.path.isfile(os.path.join(class_path, f))])
            class_counts[class_name] = file_count
            
    for class_name, count in class_counts.items():
        print(f"{class_name}: {count} images")
    
    # Analyze class balance
    total_images = sum(class_counts.values())
    print(f"Total images: {total_images}")
    
    if len(class_counts) > 0:
        max_count = max(class_counts.values())
        min_count = min(class_counts.values())
        imbalance_ratio = max_count / min_count if min_count > 0 else float('inf')
        print(f"Class imbalance ratio (max/min): {imbalance_ratio:.2f}")
        
        if imbalance_ratio > 3:
            print("Warning: Significant class imbalance detected. Consider data augmentation or balancing techniques.")
    print("========================")
    
    # Prepare data
    print("\n=== Preparing Data ===")
    train_ds, val_ds = classifier.prepare_data(validation_split=args.val_split)
    print("========================")
    
    # Build and train the model
    print("\n=== Building and Training Model ===")
    classifier.build_model(num_classes=len(classifier.class_names))
    history = classifier.train(train_ds, val_ds, epochs=args.epochs, fine_tune_at=args.fine_tune_at)
    print("========================")
    
    # Evaluate the model
    print("\n=== Evaluating Model ===")
    eval_report = classifier.evaluate(val_ds)
    
    # Print key metrics
    print("\n=== Model Performance ===")
    accuracy = eval_report['accuracy']
    print(f"Overall accuracy: {accuracy:.4f}")
    
    print("\nPer-class metrics:")
    for class_name in classifier.class_names:
        precision = eval_report[class_name]['precision']
        recall = eval_report[class_name]['recall']
        f1 = eval_report[class_name]['f1-score']
        support = eval_report[class_name]['support']
        print(f"{class_name}:")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall: {recall:.4f}")
        print(f"  F1-score: {f1:.4f}")
        print(f"  Support: {support}")
    print("========================")
    
    # Plot training history
    classifier.plot_training_history()
    
    # Save the model
    print("\n=== Saving Model ===")
    classifier.save_model(args.model_path)
    print("========================")
    
    print("\nTraining completed successfully!")

if __name__ == "__main__":
    main()