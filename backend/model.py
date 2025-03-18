import os
import numpy as np
import pandas as pd
import pickle
from collections import Counter
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, TimeDistributed, Flatten, Dense, Dropout
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import cv2
import imgaug.augmenters as iaa

# File paths
DATASET_PATH = 'backend/position.csv'
MODEL_DIR = 'models'
SKILL_MODEL_PATH = os.path.join(MODEL_DIR, 'skill_model.h5')
POSITION_MODEL_PATH = os.path.join(MODEL_DIR, 'position_model.pkl')

# Skills and Positions
POSITIONS = ['Goal Attack', 'Goal Keeper', 'Goal Shooter', 'Goal Defence', 'Wing Attack', 'Wing Defence', 'Center']
SKILLS = ['Attacking', 'Ball Handling', 'Defending', 'Footwork', 'Shooting']

# Ensure model directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

# Data Augmentation
def augment_frames(frames):
    aug = iaa.Sequential([
        iaa.Fliplr(0.5),
        iaa.Affine(rotate=(-10, 10)),
        iaa.GaussianBlur(sigma=(0, 1.0))
    ])
    return aug(images=frames)

# Video Loading & Augmentation
def load_videos_from_directory(base_dir, img_size=(64, 64), fixed_frame_count=30):
    X, y = [], []
    for label, skill in enumerate(SKILLS):
        skill_dir = os.path.join(base_dir, skill)
        if not os.path.exists(skill_dir):
            continue
        for video_file in os.listdir(skill_dir):
            video_path = os.path.join(skill_dir, video_file)
            cap = cv2.VideoCapture(video_path)
            frames = []
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame_resized = cv2.resize(frame, img_size)
                frames.append(frame_resized)
            cap.release()

            if len(frames) >= fixed_frame_count:
                frames = frames[:fixed_frame_count]
            else:
                padding = [np.zeros((img_size[0], img_size[1], 3), dtype=np.uint8)] * (fixed_frame_count - len(frames))
                frames.extend(padding)

            frames = augment_frames(frames)
            X.append(np.array(frames))
            y.append(label)
    return np.array(X), np.array(y)

# Load and preprocess video data
def load_and_preprocess_video_data(base_dir='data/videos'):
    X, y = load_videos_from_directory(base_dir)
    X = X / 255.0
    y = to_categorical(y, num_classes=len(SKILLS))
    return train_test_split(X, y, test_size=0.2, random_state=42)

# Pretrained ResNet50 for feature extraction
def train_skill_model(X_train, y_train, X_val, y_val):
    base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(64, 64, 3))
    for layer in base_model.layers[-20:]:
        layer.trainable = True

    model = Sequential([
        TimeDistributed(base_model, input_shape=(None, 64, 64, 3)),
        TimeDistributed(Flatten()),
        LSTM(64, return_sequences=True),
        LSTM(64),
        Dense(64, activation='relu'),
        Dropout(0.3),
        Dense(len(SKILLS), activation='softmax')
    ])

    model.compile(optimizer=Adam(1e-4), loss='categorical_crossentropy', metrics=['accuracy'])
    early_stopping = EarlyStopping(monitor='val_loss', patience=5)

    model.fit(X_train, y_train, validation_data=(X_val, y_val),
              epochs=70, batch_size=8, callbacks=[early_stopping])
    model.save(SKILL_MODEL_PATH)
    print("[INFO] Skill model saved successfully.")
    return model

# Load dataset for position prediction
def load_dataset():
    data = pd.read_csv(DATASET_PATH)
    skills = data[SKILLS].values
    positions = data['position'].values
    return skills, positions

# Position prediction model training
def train_position_model():
    skills, positions = load_dataset()

    # Class distribution analysis
    print("Original Class Distribution:", Counter(positions))

    # Feature scaling
    scaler = StandardScaler()
    skills_scaled = scaler.fit_transform(skills)

    # Encoding positions
    le = LabelEncoder()
    positions_encoded = le.fit_transform(positions)

    # Train-test split
    X_train, X_val, y_train, y_val = train_test_split(skills_scaled, positions_encoded,
                                                      test_size=0.2, random_state=42)

    # Class weights for imbalance
    class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
    class_weights_dict = dict(enumerate(class_weights))

    # Improved pipeline with SMOTE
    pipeline = ImbPipeline([
        ('smote', SMOTE(random_state=42)),
        ('rf', RandomForestClassifier(class_weight=class_weights_dict, random_state=42))
    ])

    # Randomized search parameters
    param_dist = {
        'rf__n_estimators': [300, 400, 500],
        'rf__max_depth': [None, 20, 30],
        'rf__min_samples_split': [2, 5],
        'rf__min_samples_leaf': [1, 3],
        'rf__max_features': ['sqrt', 'log2']
    }

    # Randomized search with scoring
    search = RandomizedSearchCV(pipeline, param_dist, n_iter=30, cv=5,
                                scoring='balanced_accuracy', verbose=2, n_jobs=-1,
                                random_state=42)
    search.fit(X_train, y_train)

    # Save best model
    best_model = search.best_estimator_
    with open(POSITION_MODEL_PATH, 'wb') as f:
        pickle.dump(best_model, f)

    # Evaluation
    y_pred = best_model.predict(X_val)
    print("\nBest Parameters:", search.best_params_)
    print("Validation Accuracy:", accuracy_score(y_val, y_pred))
    print("\nClassification Report:\n", classification_report(y_val, y_pred, target_names=POSITIONS))
    print("\nConfusion Matrix:\n", confusion_matrix(y_val, y_pred))
    print("[INFO] Position model saved successfully.")

# Predict position based on input skills
def predict_position(skills):
    with open(POSITION_MODEL_PATH, 'rb') as f:
        model = pickle.load(f)

    skills_array = np.array(list(skills.values())).reshape(1, -1)

    probabilities = model.predict_proba(skills_array)[0]
    print("[INFO] Position Probabilities:", dict(zip(POSITIONS, probabilities)))

    predicted_label = model.predict(skills_array)[0]
    return POSITIONS[predicted_label]

if __name__ == '__main__':
    X_train, X_val, y_train, y_val = load_and_preprocess_video_data()
    train_skill_model(X_train, y_train, X_val, y_val)
    train_position_model()
