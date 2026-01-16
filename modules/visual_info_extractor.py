# modules/visual_info_extractor.py

import torch
from PIL import Image
from torchvision import transforms
from torchvision.models import resnet18
from torchvision.models import ResNet18_Weights
import os
import cv2
from ultralytics import YOLO

# Load models once
yolo_model = YOLO("yolov8n.pt")  # Small and fast
scene_model = resnet18(weights=ResNet18_Weights.DEFAULT)
scene_model.eval()

# Define image transform for scene recognition
scene_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# Load ImageNet class labels for ResNet (scenes will be coarse)
imagenet_labels = ResNet18_Weights.DEFAULT.meta["categories"]

def extract_visual_info(frame_path: str):
    image = Image.open(frame_path).convert("RGB")

    # Object detection with YOLO
    yolo_results = yolo_model(frame_path)[0]
    detected_objects = list(set([yolo_results.names[int(cls)] for cls in yolo_results.boxes.cls.tolist()]))

    # Scene recognition with ResNet
    input_tensor = scene_transform(image).unsqueeze(0)
    with torch.no_grad():
        scene_logits = scene_model(input_tensor)
    scene_label = imagenet_labels[scene_logits.argmax().item()]

    return detected_objects, scene_label


def process_video_frames(video_path: str, frame_interval: int = 10):
    """
    Process video frames at 10-second intervals
    Args:
        video_path: Path to video file
        frame_interval: Interval in seconds between frames
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    results = []
    
    # Calculate frame skip based on FPS and desired interval
    frames_to_skip = int(fps * frame_interval)
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Process only frames at 10-second intervals
        if frame_count % frames_to_skip == 0:
            timestamp = round(frame_count / fps, 2)
            frame_path = f"temp_frame.jpg"
            cv2.imwrite(frame_path, frame)
            
            try:
                objects, scene = extract_visual_info(frame_path)
                results.append({
                    "timestamp": timestamp,
                    "objects": objects,
                    "scene": scene
                })
            except Exception as e:
                print(f"Error processing frame at {timestamp}s: {e}")
                
            os.remove(frame_path)
            
        frame_count += 1
        
    cap.release()
    return results
