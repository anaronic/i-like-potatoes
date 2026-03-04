import streamlit as st
from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip, ColorClip
import tempfile
import os

st.set_page_config(page_title="Potato/Tomato Reel Maker", page_icon="🥔")
st.title("🥔 Staggered Reveal Reel Maker")
st.write("Upload 4 photos to create your 'Lazy Confessions' edit.")

# --- UI Setup ---
uploaded_files = st.file_uploader("Choose 4 images", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)
# You'll need to upload the audio file too, or I can help you hardcode a link
audio_file = st.file_uploader("Upload the 'Lazy Confessions' Audio", type=['mp3', 'm4a'])

if st.button("Generate Reel") and len(uploaded_files) == 4 and audio_file:
    with st.spinner("🎬 Rendering your masterpiece... this takes about 30 seconds."):
        
        # Save uploaded files to temp locations
        temp_dir = tempfile.mkdtemp()
        img_paths = []
        for i, uploaded_file in enumerate(uploaded_files):
            path = os.path.join(temp_dir, f"img_{i}.jpg")
            with open(path, "wb") as f:
                f.write(uploaded_file.getvalue())
            img_paths.append(path)
            
        audio_path = os.path.join(temp_dir, "audio.mp3")
        with open(audio_path, "wb") as f:
            f.write(audio_file.getvalue())

        # --- Video Processing Logic ---
        beat_duration = 0.75 # Adjust to sync with your specific audio
        total_duration = beat_duration * 8
        
        layers = [ColorClip(size=(1080, 1920), color=(0,0,0)).set_duration(total_duration)]

        for i, img_path in enumerate(img_paths):
            photo_start = i * (beat_duration * 2)
            # Resize and center
            clip = ImageClip(img_path).resize(height=1920).set_duration(beat_duration * 2)
            # If photo is too wide after resizing, crop to 1080 width
            if clip.w > 1080:
                clip = clip.crop(x_center=clip.w/2, width=1080)
            
            # Left half (starts at beat 0, 2, 4, 6)
            left = clip.crop(x1=0, y1=0, x2=540, y2=1920).set_start(photo_start).set_position((0,0))
            # Right half (starts 1 beat later)
            right = clip.crop(x1=540, y1=0, x2=1080, y2=1920).set_start(photo_start + beat_duration).set_position((540,0))
            
            layers.extend([left, right])

        # Composite and Audio
        final_audio = AudioFileClip(audio_path).subclip(0, total_duration)
        final_video = CompositeVideoClip(layers, size=(1080, 1920)).set_audio(final_audio)
        
        output_path = os.path.join(temp_dir, "final_reel.mp4")
        final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

        # --- Download Button ---
        with open(output_path, "rb") as f:
            st.video(f.read())
            st.download_button("Download Reel", f, "my_couple_edit.mp4", "video/mp4")