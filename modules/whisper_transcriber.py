import whisper
import os
import moviepy.editor as mp

def extract_audio(video_path, audio_path="temp_audio.wav"):
    clip = mp.VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path)
    return audio_path

def transcribe_audio(audio_path, save_path="assets/transcripts/transcript.txt"):
    model = whisper.load_model("base")  # or "small"/"medium"
    result = model.transcribe(audio_path)
    transcript = result["text"]

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # Save transcript to a file
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(transcript)

    return transcript
