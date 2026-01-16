import os
import sys

# Disable Streamlit's file watcher
os.environ['STREAMLIT_SERVER_WATCH_DIRS'] = 'false'
os.environ['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'none'

# Block torch.classes from being watched
class TorchClassesImportBlocker:
    def find_spec(self, fullname, path, target=None):
        if fullname.startswith('torch.classes'):
            return None
        return None

sys.meta_path.insert(0, TorchClassesImportBlocker())

# Now import streamlit and other dependencies
import streamlit as st
import time
from modules.frame_extraction import extract_frames
from modules.clip_selector import select_keyframes_and_remove_others
from modules.whisper_transcriber import extract_audio, transcribe_audio
from modules.text_summarizer import summarize_text
from modules.visual_info_extractor import process_video_frames
from modules.video_summarizer import extract_timestamps_from_summary, create_video_summary

# Force disable watchdog usage
if 'STREAMLIT_SERVER_FILE_WATCHER_TYPE' not in os.environ:
    os.environ['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'none'

# Set page config
st.set_page_config(
    page_title="AI Video Summarizer",
    layout="wide",
    page_icon="🎬"
)

# CSS Styling
st.markdown("""
    <style>
        body {
            background-color: #0F0F0F;
            color: #FFFFFF;
        }
        .main {
            background-color: #0F0F0F;
        }
        h1, h2, h3 {
            color: #FFD700;
        }
        .box {
            background-color: #1E1E1E;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.4);
            margin-bottom: 20px;
            width: 100%;
        }
        .stButton > button {
            background: linear-gradient(to right, #FFD700, #FFA500);
            border: none;
            color: black;
            font-weight: bold;
            padding: 10px 24px;
            border-radius: 8px;
            transition: 0.3s;
        }
        .stButton > button:hover {
            transform: scale(1.03);
        }
        .three-box {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        .three-box > div {
            flex: 1;
            min-width: 300px;
        }
        .stTextArea textarea {
            background-color: #2B2B2B !important;
            color: white !important;
            border: 1px solid #444 !important;
            border-radius: 8px !important;
        }
        .download-btn {
            margin-top: 10px;
        }
    </style>
""", unsafe_allow_html=True)

def process_video_file(video_path, frame_output, progress_bar):
    """Process video with progress updates"""
    try:
        # Extract frames (20%) - now 1 frame every 10 seconds
        progress_bar.progress(10)
        extract_frames(video_path, frame_output, frame_interval=10)  # Changed from 100 to 10
        
        # Select keyframes (40%)
        progress_bar.progress(30)
        selected_keyframes = select_keyframes_and_remove_others(frame_output, keep_ratio=0.3)
        
        # Extract visual information (60%) - now 1 frame every 10 seconds
        progress_bar.progress(50)
        visual_info_list = process_video_frames(video_path, frame_interval=10)  # Changed from 10 to 10 seconds
        
        # Extract and transcribe audio (80%)
        progress_bar.progress(70)
        audio_path = extract_audio(video_path)
        transcript = transcribe_audio(audio_path)
        
        # Create summary (90%)
        progress_bar.progress(85)
        summary = summarize_text(transcript)
        
        # Extract timestamps and create video summary (100%)
        timestamps = extract_timestamps_from_summary(summary, visual_info_list)
        summary_video = create_video_summary(
            video_path, 
            timestamps, 
            min_clip_duration=15,
            include_start=True,
            start_duration=5,
            target_ratio=0.3
        )
        
        summary_video_path = "assets/output/video_summary.mp4"
        os.makedirs(os.path.dirname(summary_video_path), exist_ok=True)  # Ensure directory exists
        summary_video.write_videofile(summary_video_path, 
                                    codec='libx264', 
                                    audio_codec='aac',
                                    fps=24)
        
        progress_bar.progress(100)
        
        return summary, transcript, visual_info_list, summary_video_path
        
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None, None, None, None

# Header
st.markdown("""
    <div style="text-align: center;">
        <h1>🎬 AI Video Summarizer</h1>
        <p style="color: #AAAAAA;">Summarize long videos with AI in seconds</p>
    </div>
    <hr style="border-top: 2px solid #FFD700; margin-bottom: 30px;">
""", unsafe_allow_html=True)

# Upload section
st.markdown("### 📤 Upload Video")
uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mkv"])

if uploaded_file:
    st.success(f"Uploaded: {uploaded_file.name}")
    
    # Display original video
    st.markdown("#### ▶ Input Video")
    st.video(uploaded_file)
    
    col1, col2 = st.columns(2)
    with col1:
        process = st.button("⚡ Process Video")
    with col2:
        clear = st.button("🧹 Clear")
    
    if process:
        # Save uploaded file temporarily
        temp_path = f"assets/input_videos/{uploaded_file.name}"
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        frame_output = "assets/keyframes"
        os.makedirs(frame_output, exist_ok=True)
        
        progress_bar = st.progress(0)
        
        with st.spinner("Processing video..."):
            summary, transcript, visual_info, summary_video_path = process_video_file(
                temp_path, frame_output, progress_bar
            )
        
        if summary and transcript and visual_info:
            # Format visual info for display
            topics = "\n".join([f"• {info}" for info in visual_info[:5]])
            
            # Output section
            st.markdown("### 🔍 Results")
            
            # Display summary video
            if os.path.exists(summary_video_path):
                st.markdown("#### 🎥 Video Summary")
                st.video(summary_video_path)
            
            # Create three columns for the boxes
            col1, col2, col3 = st.columns(3)
            
            # Summary box
            with col1:
                st.markdown('<div class="box">', unsafe_allow_html=True)
                st.markdown("#### 📌 Summary")
                st.text_area("", summary, height=200)
                st.markdown('<div class="download-btn">', unsafe_allow_html=True)
                st.download_button("📥 Download Summary", summary, file_name="summary.txt")
                st.markdown('</div></div>', unsafe_allow_html=True)
            
            # Transcript box
            with col2:
                st.markdown('<div class="box">', unsafe_allow_html=True)
                st.markdown("#### 📜 Transcript")
                st.text_area("", transcript, height=200)
                st.markdown('<div class="download-btn">', unsafe_allow_html=True)
                st.download_button("📥 Download Transcript", transcript, file_name="transcript.txt")
                st.markdown('</div></div>', unsafe_allow_html=True)
            
            # Visual info box
            with col3:
                st.markdown('<div class="box">', unsafe_allow_html=True)
                st.markdown("#### 🧠 Key Visual Elements")
                st.text_area("", topics, height=200)
                st.markdown('<div class="download-btn">', unsafe_allow_html=True)
                st.download_button("📥 Download Topics", topics, file_name="visual_elements.txt")
                st.markdown('</div></div>', unsafe_allow_html=True)
            
    elif clear:
        st.experimental_rerun()

else:
    st.info("Upload a video file to get started.")

# Footer
st.markdown("""
    <hr style="border-top: 2px solid #FFD700;">
    <div style="text-align: center; color: #888888;">
        AI-Based Video Summarizer | Built with Streamlit 🚀
    </div>
""", unsafe_allow_html=True)
