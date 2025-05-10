import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import MobileNet
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import TimeDistributed, LSTM, Dense, Dropout, Flatten
from tensorflow.keras.utils import to_categorical, Sequence
from sklearn.model_selection import train_test_split

# Define constants
DATASET_PATH = "D:\Y4S1\RESEARCH\PP1-Finals\Dataset"
CLASSES = ['360_rotation', 'In_out', 'Squat']
FRAME_SIZE = (128, 128)
SEQ_LENGTH = 30  # Number of frames per video
BATCH_SIZE = 8
EPOCHS = 20

# Preprocess video data
def preprocess_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, FRAME_SIZE)
        frames.append(frame)
    cap.release()
    frames = np.array(frames)
    # Select SEQ_LENGTH evenly spaced frames
    if len(frames) >= SEQ_LENGTH:
        indices = np.linspace(0, len(frames) - 1, SEQ_LENGTH).astype(int)
        frames = frames[indices]
    else:
        # Pad with black frames if video is shorter
        pad_len = SEQ_LENGTH - len(frames)
        frames = np.pad(frames, ((0, pad_len), (0, 0), (0, 0), (0, 0)), mode='constant')
    return frames / 255.0  # Normalize

# Load dataset paths
def load_dataset_paths():
    video_paths = []
    labels = []
    for class_id, class_name in enumerate(CLASSES):
        class_path = os.path.join(DATASET_PATH, class_name)
        for video_file in os.listdir(class_path):
            video_path = os.path.join(class_path, video_file)
            video_paths.append(video_path)
            labels.append(class_id)
    return video_paths, labels

# Define VideoDataGenerator
class VideoDataGenerator(Sequence):
    def __init__(self, video_paths, labels, batch_size):
        self.video_paths = video_paths
        self.labels = labels
        self.batch_size = batch_size
    
    def __len__(self):
        return int(np.ceil(len(self.video_paths) / self.batch_size))
    
    def __getitem__(self, idx):
        batch_paths = self.video_paths[idx * self.batch_size:(idx + 1) * self.batch_size]
        batch_labels = self.labels[idx * self.batch_size:(idx + 1) * self.batch_size]
        
        X, y = [], []
        for video_path, label in zip(batch_paths, batch_labels):
            X.append(preprocess_video(video_path))
            y.append(label)
        
        return np.array(X), to_categorical(np.array(y), num_classes=len(CLASSES))

# Prepare data
video_paths, labels = load_dataset_paths()
train_paths, test_paths, train_labels, test_labels = train_test_split(
    video_paths, labels, test_size=0.2, random_state=42
)

train_generator = VideoDataGenerator(train_paths, train_labels, batch_size=BATCH_SIZE)
test_generator = VideoDataGenerator(test_paths, test_labels, batch_size=BATCH_SIZE)

# Feature extraction model (CNN)
cnn = MobileNet(weights='imagenet', include_top=False, input_shape=(FRAME_SIZE[0], FRAME_SIZE[1], 3))
cnn.trainable = False

# Build sequence model,flatten is used
model = Sequential([
    TimeDistributed(cnn, input_shape=(SEQ_LENGTH, FRAME_SIZE[0], FRAME_SIZE[1], 3)),
    TimeDistributed(Flatten()),
    LSTM(64, return_sequences=False),
    Dropout(0.5),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(len(CLASSES), activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Train model with generators
model.fit(train_generator, validation_data=test_generator, epochs=EPOCHS)

# Save model
model.save("exercise_classification_model.keras")

print("Model training complete and saved.")



