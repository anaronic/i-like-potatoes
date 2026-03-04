import streamlit as st
from moviepy import ImageClip, CompositeVideoClip, AudioFileClip, ColorClip
import tempfile
import os

st.title("🥔 8-Photo Potato/Tomato Reveal (v2.0)")

# 1. Path to your file in the GitHub repo
AUDIO_PATH = "song.mp3" 

uploaded_files = st.file_uploader("Upload 8 Photos", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

if st.button("Generate Reel"):
    if len(uploaded_files) != 8:
        st.error("Please upload exactly 8 photos!")
    elif not os.path.isfile(AUDIO_PATH):
        st.error(f"Error: '{AUDIO_PATH}' not found in repo. Check filename casing!")
    else:
        with st.spinner("🎬 Syncing to the beat..."):
            # 2. Save Images to Temp
            temp_dir = tempfile.mkdtemp()
            img_paths = []
            
            # Use the order they were uploaded
            for i, uploaded_file in enumerate(uploaded_files):
                path = os.path.join(temp_dir, f"img_{i}.jpg")
                with open(path, "wb") as f:
                    f.write(uploaded_file.read())
                img_paths.append(path)

            # 3. Timing Logic
            beat_duration = 0.75 
            total_duration = beat_duration * 8
            
            # Create the black background layer
            bg = ColorClip(size=(1080, 1920), color=(0,0,0)).with_duration(total_duration)
            layers = [bg]

            for i, path in enumerate(img_paths):
                start_time = i * beat_duration
                
                # Setup clip (9:16) - Using v2.0 .with_duration()
                clip = ImageClip(path).with_duration(beat_duration).resized(height=1920)
                
                # Center crop if too wide
                if clip.w > 1080:
                    clip = clip.cropped(x_center=clip.w/2, width=1080)

                # Reveal Left then Right
                # .with_start() and .with_position() are the v2.0 standard
                left = (clip.cropped(x1=0, y1=0, x2=540, y2=1920)
                        .with_start(start_time)
                        .with_position((0,0)))
                
                right_offset = beat_duration * 0.4 
                right = (clip.cropped(x1=540, y1=0, x2=1080, y2=1920)
                         .with_start(start_time + right_offset)
                         .with_position((540,0)))
                
                layers.extend([left, right])

            # 4. Audio & Final Export
            audio = AudioFileClip(AUDIO_PATH).with_section(0, total_duration)
            final_vid = CompositeVideoClip(layers, size=(1080, 1920)).with_audio(audio)
            
            out_file = os.path.join(temp_dir, "final_reel.mp4")
            
            # MoviePy 2.0 still uses write_videofile
            final_vid.write_videofile(out_file, fps=24, codec="libx264", audio_codec="aac")

            # 5. Display
            st.video(out_file)
            st.download_button("Download Reel", open(out_file, "rb"), "potato_tomato.mp4")