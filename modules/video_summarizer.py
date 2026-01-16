from moviepy.editor import VideoFileClip, concatenate_videoclips
import re

def merge_nearby_timestamps(timestamps, min_gap=10):
    """Merge timestamps that are too close to each other"""
    if not timestamps:
        return []
    
    # Sort timestamps first
    sorted_times = sorted(timestamps)
    merged = []
    current = sorted_times[0]
    
    for next_time in sorted_times[1:]:
        if next_time - current < min_gap:
            continue
        merged.append(current)
        current = next_time
    
    merged.append(current)
    return merged

def extract_timestamps_from_summary(summary_text, min_gap=10):
    """Extract timestamps from summary text and remove redundant ones"""
    timestamps = []
    lines = summary_text.split('\n')
    
    for line in lines:
        if '[' in line and ']' in line:
            try:
                time_str = line[line.find('[')+1:line.find(']')]
                minutes, seconds = map(int, time_str.split(':'))
                timestamp = minutes * 60 + seconds
                timestamps.append(timestamp)
            except Exception as e:
                print(f"Error parsing timestamp from line: {line}")
                continue
    
    # Remove duplicates, sort, and merge nearby timestamps
    return merge_nearby_timestamps(timestamps, min_gap)

def create_video_summary(video_path, timestamps, min_clip_duration=15, include_start=False, start_duration=5, target_ratio=0.3):
    """
    Create a summary video from timestamps
    target_ratio: target duration ratio compared to original video (default 0.3 = 30% of original)
    """
    video = VideoFileClip(video_path)
    clips = []
    last_end_time = 0
    max_summary_duration = video.duration * target_ratio
    current_duration = 0
    
    # Sort timestamps to ensure chronological order
    timestamps = sorted(timestamps)
    
    # Handle start clip first if needed
    if include_start:
        start_clip = video.subclip(0, min(start_duration, video.duration))
        clips.append(start_clip)
        current_duration = start_duration
        last_end_time = start_duration

    # Process each timestamp
    for timestamp in timestamps:
        # Skip if timestamp is too close to last clip
        if timestamp < last_end_time + 2:  # 2-second buffer
            continue
            
        start_time = max(timestamp - min_clip_duration/2, last_end_time)
        end_time = min(timestamp + min_clip_duration/2, video.duration)
        
        # Skip if clip duration is too short
        if end_time - start_time < 5:  # Minimum 5 seconds
            continue
            
        clip = video.subclip(start_time, end_time)
        clips.append(clip)
        current_duration += (end_time - start_time)
        last_end_time = end_time
        
        # Check if we've reached target duration
        if current_duration >= max_summary_duration:
            break
    
    # If no clips were selected, take evenly spaced clips
    if not clips:
        total_clips = int(video.duration / min_clip_duration)
        interval = video.duration / total_clips
        for i in range(total_clips):
            start = i * interval
            end = min(start + min_clip_duration, video.duration)
            clips.append(video.subclip(start, end))
    
    # Concatenate all clips
    final_video = concatenate_videoclips(clips)
    return final_video










