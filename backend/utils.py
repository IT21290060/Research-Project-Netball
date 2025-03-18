import cv2
import os
import numpy as np

def extract_frames(video_path, frame_rate=1, max_frames=30, img_size=(64, 64)):
    """Extract a fixed number of frames from the video at the specified frame rate.
    
    Args:
        video_path (str): Path to the video file.
        frame_rate (int): The rate at which to extract frames (every nth frame).
        max_frames (int): The maximum number of frames to extract.
        img_size (tuple): The size to which each frame will be resized.

    Returns:
        np.ndarray: An array of extracted frames.
    """
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        raise ValueError(f"Error: Could not open video file {video_path}")
    
    frames = []
    count = 0
    success, image = video.read()
    
    while success and len(frames) < max_frames:
        if count % frame_rate == 0:
            # Resize the frame to the desired input size
            resized_frame = cv2.resize(image, img_size)
            frames.append(resized_frame)
        success, image = video.read()
        count += 1
    
    video.release()
    
    # Ensure we have exactly `max_frames` by padding with black frames if needed
    if len(frames) < max_frames:
        padding_frames = [np.zeros((img_size[0], img_size[1], 3), dtype=np.uint8)] * (max_frames - len(frames))
        frames.extend(padding_frames)
    
    return np.array(frames)

def process_uploaded_video(video_path, output_path):
    """Process the uploaded video for analysis by extracting frames.
    
    Args:
        video_path (str): Path to the uploaded video.
        output_path (str): Directory where extracted frames will be saved.

    Returns:
        np.ndarray: An array of extracted frames.
    """
    # Ensure output directory exists
    os.makedirs(output_path, exist_ok=True)
    
    # Extract frames from the video
    frames = extract_frames(video_path)
    
    # Save extracted frames as images in the output directory
    for i, frame in enumerate(frames):
        cv2.imwrite(os.path.join(output_path, f"frame_{i}.jpg"), frame)
    
    return frames
