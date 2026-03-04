import streamlit as st
from moviepy import ImageClip, CompositeVideoClip, AudioFileClip, ColorClip
import tempfile
import os

st.title("🥔 17s Staggered Reveal (16 Intervals)")

AUDIO_PATH = "song.mp3" 

uploaded_files = st.file_uploader("Upload 8 Photos", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

if st.button("Generate 17s Reel"):
    if len(uploaded_files) != 8:
        st.error("Please upload exactly 8 photos!")
    elif not os.path.isfile(AUDIO_PATH):
        st.error(f"'{AUDIO_PATH}' not found in GitHub!")
    else:
        with st.spinner("🎬 Syncing to 16 intervals..."):
            temp_dir = tempfile.mkdtemp()
            img_paths = []
            
            # Use original upload order
            for i, uploaded_file in enumerate(uploaded_files):
                path = os.path.join(temp_dir, f"img_{i}.jpg")
                with open(path, "wb") as f:
                    f.write(uploaded_file.read())
                img_paths.append(path)

            # --- MATH REFACTOR ---
            total_audio_length = 17.0
            num_intervals = 16
            interval_duration = total_audio_length / num_intervals # 1.0625s
            photo_duration = interval_duration * 2                # 2.125s
            
            # Black Background
            bg = ColorClip(size=(1080, 1920), color=(0,0,0)).with_duration(total_audio_length)
            layers = [bg]

            for i, path in enumerate(img_paths):
                # Each photo starts at interval 0, 2, 4, 6...
                photo_start_time = i * photo_duration
                
                # Setup Image
                clip = ImageClip(path).with_duration(photo_duration).resized(height=1920)
                if clip.w > 1080:
                    clip = clip.cropped(x_center=clip.w/2, width=1080)

                # INTERVAL 1 of the photo: Left Only
                left = (clip.cropped(x1=0, y1=0, x2=540, y2=1920)
                        .with_start(photo_start_time)
                        .with_position((0, 0)))
                
                # INTERVAL 2 of the photo: Right fills in
                # It starts exactly one interval (1.06s) after the left side
                right = (clip.cropped(x1=540, y1=0, x2=1080, y2=1920)
                         .with_start(photo_start_time + interval_duration)
                         .with_position((540, 0)))
                
                layers.extend([left, right])

            # --- AUDIO & EXPORT ---
            audio = AudioFileClip(AUDIO_PATH).subclipped(0, total_audio_length)
            final_vid = CompositeVideoClip(layers, size=(1080, 1920)).with_audio(audio)
            
            out_file = os.path.join(temp_dir, "final_17s_reel.mp4")
            final_vid.write_videofile(out_file, fps=24, codec="libx264", audio_codec="aac")

            st.video(out_file)
            st.download_button("Download Reel", open(out_file, "rb"), "potato_17s.mp4")