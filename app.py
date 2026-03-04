import streamlit as st
from moviepy import ImageClip, CompositeVideoClip, AudioFileClip, ColorClip
import tempfile
import os

st.set_page_config(page_title="Potato Reveal 2.0", page_icon="🥔")
st.title("🥔 8-Photo Staggered Reveal")

# Ensure this file exists in your GitHub root!
AUDIO_PATH = "song.mp3" 

uploaded_files = st.file_uploader("Upload 8 Photos", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

if st.button("Generate Reel"):
    if len(uploaded_files) != 8:
        st.error("Please upload exactly 8 photos!")
    elif not os.path.isfile(AUDIO_PATH):
        st.error(f"File '{AUDIO_PATH}' not found in GitHub. Please check the filename.")
    else:
        with st.spinner("🎬 MoviePy 2.0 is rendering..."):
            temp_dir = tempfile.mkdtemp()
            img_paths = []
            
            # Save images to temp folder
            for i, uploaded_file in enumerate(uploaded_files):
                path = os.path.join(temp_dir, f"img_{i}.jpg")
                with open(path, "wb") as f:
                    f.write(uploaded_file.read())
                img_paths.append(path)

            # --- VIDEO PARAMETERS ---
            beat_duration = 0.75 
            total_duration = beat_duration * 8
            
            # Background (Black Canvas)
            bg = ColorClip(size=(1080, 1920), color=(0,0,0)).with_duration(total_duration)
            layers = [bg]

            for i, path in enumerate(img_paths):
                start_time = i * beat_duration
                
                # Setup Image Clip
                # resized() and with_duration() are the 2.0 standard
                clip = ImageClip(path).with_duration(beat_duration).resized(height=1920)
                
                # Center crop to 9:16 ratio if necessary
                if clip.w > 1080:
                    clip = clip.cropped(x_center=clip.w/2, width=1080)

                # 1. Left half: pops in at the start of the beat
                left = (clip.cropped(x1=0, y1=0, x2=540, y2=1920)
                        .with_start(start_time)
                        .with_position((0, 0)))
                
                # 2. Right half: pops in 40% through the beat to create the "reveal"
                right_offset = beat_duration * 0.4 
                right = (clip.cropped(x1=540, y1=0, x2=1080, y2=1920)
                         .with_start(start_time + right_offset)
                         .with_position((540, 0)))
                
                layers.extend([left, right])

            # --- AUDIO HANDLING ---
            # subclipped() is the official 2.0 replacement for subclip()
            audio = AudioFileClip(AUDIO_PATH).subclipped(0, total_duration)
            
            # Composite and Attach Audio
            final_vid = CompositeVideoClip(layers, size=(1080, 1920)).with_audio(audio)
            
            out_file = os.path.join(temp_dir, "final_reel.mp4")
            
            # Export (using libx264 for Instagram/TikTok compatibility)
            final_vid.write_videofile(out_file, fps=24, codec="libx264", audio_codec="aac")

            # --- OUTPUT ---
            st.video(out_file)
            st.download_button("Download Video", open(out_file, "rb"), "potato_reveal.mp4")