# modules/frame_extraction.py
import cv2
import os

def extract_frames(video_path, output_dir, frame_interval=3):
    """
    Extract frames from video at specified time intervals
    Args:
        video_path: Path to video file
        output_dir: Directory to save extracted frames
        frame_interval: Interval in seconds between frames
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Calculate frame skip based on FPS and desired interval
    frames_to_skip = int(fps * frame_interval)
    frame_count = 0
    saved_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Save frame every 10 seconds
        if frame_count % frames_to_skip == 0:
            filename = os.path.join(output_dir, f"frame_{saved_count:05d}.jpg")
            cv2.imwrite(filename, frame)
            saved_count += 1

        frame_count += 1

    cap.release()
    return saved_count
