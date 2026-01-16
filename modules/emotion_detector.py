# modules/emotion_detector.py

from deepface import DeepFace
import os

def detect_emotions_in_folder(folder_path):
    emotion_results = {}

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        try:
            result = DeepFace.analyze(img_path=file_path, actions=['emotion'], enforce_detection=False)
            dominant_emotion = result[0]['dominant_emotion']
            emotion_results[file_name] = dominant_emotion
        except Exception as e:
            emotion_results[file_name] = f"Error: {str(e)}"

    return emotion_results
