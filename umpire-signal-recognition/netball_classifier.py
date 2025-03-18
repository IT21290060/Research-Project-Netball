import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import cv2
import json

class NetballHandSignalClassifier:
    def __init__(self, data_dir, img_height=224, img_width=224, batch_size=32, model_path=None):
        """
        Initialize the Netball Hand Signal Classifier.
        
        Args:
            data_dir (str): Directory containing the dataset
            img_height (int): Image height for resizing
            img_width (int): Image width for resizing
            batch_size (int): Batch size for training
            model_path (str): Path to load a pre-trained model (optional)
        """
        self.data_dir = data_dir
        self.img_height = img_height
        self.img_width = img_width
        self.batch_size = batch_size
        self.model = None
        self.class_names = None
        self.history = None
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
            
    def prepare_data(self, validation_split=0.2):
        """
        Prepare and augment training and validation data.
        
        Args:
            validation_split (float): Fraction of data to use for validation
            
        Returns:
            train_ds, val_ds: Training and validation datasets
        """
        print("Preparing data...")
        
        # Data augmentation for training
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            validation_split=validation_split,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest'
        )
        
        # Only rescaling for validation
        validation_datagen = ImageDataGenerator(
            rescale=1./255,
            validation_split=validation_split
        )
        
        # Load training data with augmentation
        train_ds = train_datagen.flow_from_directory(
            self.data_dir,
            target_size=(self.img_height, self.img_width),
            batch_size=self.batch_size,
            class_mode='categorical',
            subset='training',
            shuffle=True
        )
        
        # Load validation data
        val_ds = validation_datagen.flow_from_directory(
            self.data_dir,
            target_size=(self.img_height, self.img_width),
            batch_size=self.batch_size,
            class_mode='categorical',
            subset='validation',
            shuffle=False
        )
        
        # Store class names
        self.class_names = list(train_ds.class_indices.keys())
        print(f"Classes found: {self.class_names}")
        print(f"Class distribution: {train_ds.class_indices}")
        print(f"Total training samples: {train_ds.samples}")
        print(f"Total validation samples: {val_ds.samples}")
        
        return train_ds, val_ds
    
    def build_model(self, num_classes=3):
        """
        Build a transfer learning model based on MobileNetV2.
        
        Args:
            num_classes (int): Number of classes to predict
            
        Returns:
            model: The compiled Keras model
        """
        print("Building model...")
        
        # Use MobileNetV2 as the base model (good balance of accuracy and speed)
        base_model = MobileNetV2(
            input_shape=(self.img_height, self.img_width, 3),
            include_top=False,
            weights='imagenet'
        )
        
        # Freeze the base model layers
        base_model.trainable = False
        
        # Create the model
        model = models.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dropout(0.2),  # Add dropout to reduce overfitting
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(num_classes, activation='softmax')
        ])
        
        # Compile the model
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        model.summary()
        self.model = model
        return model
    
    def train(self, train_ds, val_ds, epochs=20, fine_tune_at=10):
        """
        Train the model with early stopping and learning rate reduction.
        
        Args:
            train_ds: Training dataset
            val_ds: Validation dataset
            epochs (int): Number of epochs to train
            fine_tune_at (int): Epoch to start fine-tuning from
            
        Returns:
            history: Training history
        """
        if self.model is None:
            self.build_model(num_classes=len(self.class_names))
        
        print("Training model...")
        
        # Define callbacks
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor='val_accuracy',
                patience=5,
                restore_best_weights=True
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.2,
                patience=3,
                min_lr=0.00001
            )
        ]
        
        # Initial training phase
        print("Phase 1: Training top layers...")
        history1 = self.model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=fine_tune_at,
            callbacks=callbacks
        )
        
        # Fine-tuning phase: unfreeze the top layers of the base model
        print("Phase 2: Fine-tuning model...")
        base_model = self.model.layers[0]
        base_model.trainable = True
        
        # Freeze the bottom layers and unfreeze the top layers
        for layer in base_model.layers[:-4]:
            layer.trainable = False
            
        # Recompile the model with a lower learning rate
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Continue training with fine-tuning
        history2 = self.model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=epochs,
            initial_epoch=history1.epoch[-1] + 1,
            callbacks=callbacks
        )
        
        # Combine histories
        combined_history = {}
        for k in history1.history.keys():
            combined_history[k] = history1.history[k] + history2.history[k]
            
        self.history = combined_history
        return combined_history
    
    def evaluate(self, test_ds):
        """
        Evaluate the model on test data.
        
        Args:
            test_ds: Test dataset
            
        Returns:
            report: Classification report
        """
        if self.model is None:
            raise ValueError("Model not trained or loaded.")
            
        print("Evaluating model...")
        
        # Get predictions
        y_pred_prob = self.model.predict(test_ds)
        y_pred = np.argmax(y_pred_prob, axis=1)
        
        # Get true labels
        y_true = test_ds.classes
        
        # Generate classification report
        class_names = list(test_ds.class_indices.keys())
        report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True)
        print(classification_report(y_true, y_pred, target_names=class_names))
        
        # Generate confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        self.plot_confusion_matrix(cm, class_names)
        
        return report
    
    def plot_confusion_matrix(self, cm, class_names):
        """
        Plot confusion matrix.
        
        Args:
            cm: Confusion matrix
            class_names: List of class names
        """
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
        plt.xlabel('Predicted')
        plt.ylabel('True')
        plt.title('Confusion Matrix')
        plt.savefig('confusion_matrix.png')
        plt.close()
    
    def plot_training_history(self):
        """
        Plot training and validation accuracy/loss.
        """
        if self.history is None:
            raise ValueError("Model not trained yet.")
            
        plt.figure(figsize=(12, 5))
        
        # Plot accuracy
        plt.subplot(1, 2, 1)
        plt.plot(self.history['accuracy'], label='Training Accuracy')
        plt.plot(self.history['val_accuracy'], label='Validation Accuracy')
        plt.title('Model Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend()
        
        # Plot loss
        plt.subplot(1, 2, 2)
        plt.plot(self.history['loss'], label='Training Loss')
        plt.plot(self.history['val_loss'], label='Validation Loss')
        plt.title('Model Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig('training_history.png')
        plt.close()
    
    def save_model(self, model_path='netball_model'):
        """
        Save the model.
        
        Args:
            model_path (str): Path to save the model
        """
        if self.model is None:
            raise ValueError("Model not trained or loaded.")
            
        # Save the model
        self.model.save(model_path)
        
        # Save class names to properly map predictions
        with open(f"{model_path}/class_names.json", 'w') as f:
            json.dump(self.class_names, f)
            
        print(f"Model saved to {model_path}")
    
    def load_model(self, model_path):
        """
        Load a pre-trained model.
        
        Args:
            model_path (str): Path to the saved model
        """
        if not os.path.exists(model_path):
            raise ValueError(f"Model path {model_path} does not exist.")
            
        # Load the model
        self.model = tf.keras.models.load_model(model_path)
        
        # Load class names
        class_names_path = f"{model_path}/class_names.json"
        if os.path.exists(class_names_path):
            with open(class_names_path, 'r') as f:
                self.class_names = json.load(f)
        else:
            print("Warning: class_names.json not found. Predictions may not be properly labeled.")
            
        print(f"Model loaded from {model_path}")
    
    def preprocess_image(self, image_path):
        """
        Preprocess a single image for prediction.
        
        Args:
            image_path (str): Path to the image
            
        Returns:
            img: Preprocessed image
        """
        # Read and preprocess the image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image from {image_path}")
            
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (self.img_width, self.img_height))
        img = img / 255.0
        img = np.expand_dims(img, axis=0)
        
        return img
    
    def predict(self, image_path, threshold=0.7):
        """
        Predict the class of a single image.
        
        Args:
            image_path (str): Path to the image
            threshold (float): Confidence threshold for predictions
            
        Returns:
            prediction: Dictionary with prediction results
        """
        if self.model is None:
            raise ValueError("Model not trained or loaded.")
            
        if self.class_names is None:
            raise ValueError("Class names not set. Cannot map predictions.")
            
        try:
            # Preprocess the image
            img = self.preprocess_image(image_path)
            
            # Make prediction
            pred = self.model.predict(img)[0]
            pred_class_idx = np.argmax(pred)
            confidence = float(pred[pred_class_idx])
            
            # Get prediction label
            pred_class = self.class_names[pred_class_idx]
            
            # Check if it's a valid signal or not
            if confidence < threshold:
                pred_class = "Not a Valid Umpire Hand Signal"
            
            # Create prediction results
            prediction = {
                'class': pred_class,
                'confidence': confidence,
                'above_threshold': confidence >= threshold,
                'all_probabilities': {self.class_names[i]: float(pred[i]) for i in range(len(self.class_names))}
            }
            
            # Add feedback based on confidence
            if confidence >= threshold:
                prediction['feedback'] = f"Detection confidence is high ({confidence:.2f}). Signal is {pred_class}."
            elif confidence >= threshold/2:
                prediction['feedback'] = f"Detection confidence is moderate ({confidence:.2f}). Signal might be {pred_class}, but verify."
            else:
                prediction['feedback'] = f"Detection confidence is low ({confidence:.2f}). Cannot reliably identify the signal."
                
            return prediction
            
        except Exception as e:
            # Handle errors and return a default response
            print(f"Error predicting image: {str(e)}")
            return {
                'class': 'Not a Valid Umpire Hand Signal',
                'confidence': 0.0,
                'above_threshold': False,
                'feedback': f"Error processing image: {str(e)}",
                'all_probabilities': {}
            }