import streamlit as st
from moviepy import ImageClip, CompositeVideoClip, AudioFileClip, ColorClip
import tempfile
import os

st.title("🥔 16.54s Sync: 8 Photos / 16 Intervals")

AUDIO_PATH = "song.mp3" 

uploaded_files = st.file_uploader("Upload 8 Photos", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

if st.button("Generate Sync'd Reel"):
    if len(uploaded_files) != 8:
        st.error("Please upload exactly 8 photos!")
    elif not os.path.isfile(AUDIO_PATH):
        st.error(f"'{AUDIO_PATH}' not found in GitHub!")
    else:
        with st.spinner("🎬 Calculating exact millisecond sync..."):
            temp_dir = tempfile.mkdtemp()
            img_paths = []
            
            for i, uploaded_file in enumerate(uploaded_files):
                path = os.path.join(temp_dir, f"img_{i}.jpg")
                with open(path, "wb") as f:
                    f.write(uploaded_file.read())
                img_paths.append(path)

            # --- PRECISE MATH ---
            total_duration = 16.54
            num_intervals = 16
            interval_len = total_duration / num_intervals # 1.03375s
            photo_len = interval_len * 2                  # 2.0675s
            
            bg = ColorClip(size=(1080, 1920), color=(0,0,0)).with_duration(total_duration)
            layers = [bg]

            for i, path in enumerate(img_paths):
                # Start time for this specific photo
                p_start = i * photo_len
                
                # Image setup
                clip = ImageClip(path).with_duration(photo_len).resized(height=1920)
                if clip.w > 1080:
                    clip = clip.cropped(x_center=clip.w/2, width=1080)

                # Reveal Logic
                # Left half: Starts at p_start, lasts for photo_len
                left = (clip.cropped(x1=0, y1=0, x2=540, y2=1920)
                        .with_start(p_start)
                        .with_position((0, 0)))
                
                # Right half: Starts 1 interval later, lasts until the end of photo_len
                # In MoviePy 2.0, duration is relative to the clip, 
                # so the right half's duration is the remaining half of the photo's time.
                right = (clip.cropped(x1=540, y1=0, x2=1080, y2=1920)
                         .with_duration(interval_len) 
                         .with_start(p_start + interval_len)
                         .with_position((540, 0)))
                
                layers.extend([left, right])

            # --- AUDIO & EXPORT ---
            audio = AudioFileClip(AUDIO_PATH).subclipped(0, total_duration)
            final_vid = CompositeVideoClip(layers, size=(1080, 1920)).with_audio(audio)
            
            out_file = os.path.join(temp_dir, "sync_reel.mp4")
            # Using high-quality preset for better social media compression
            final_vid.write_videofile(out_file, fps=24, codec="libx264", audio_codec="aac")

            st.video(out_file)
            st.download_button("Download Reel", open(out_file, "rb"), "potato_sync.mp4")