import streamlit as st
from moviepy import ImageClip, CompositeVideoClip, AudioFileClip, ColorClip
import tempfile
import os

st.set_page_config(page_title="Potato Reveal 4:5", page_icon="🥔")
st.title("🥔 8-Photo Sync (4:5 Ratio)")

AUDIO_PATH = "song.mp3" 

uploaded_files = st.file_uploader("Upload 8 Photos", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

if st.button("Generate 4:5 Reel"):
    if len(uploaded_files) != 8:
        st.error("Please upload exactly 8 photos!")
    elif not os.path.isfile(AUDIO_PATH):
        st.error(f"'{AUDIO_PATH}' not found in GitHub!")
    else:
        with st.spinner("🎬 Rendering in 4:5 Social Format..."):
            temp_dir = tempfile.mkdtemp()
            img_paths = []
            
            for i, uploaded_file in enumerate(uploaded_files):
                path = os.path.join(temp_dir, f"img_{i}.jpg")
                with open(path, "wb") as f:
                    f.write(uploaded_file.read())
                img_paths.append(path)

            # --- DIMENSIONS & TIMING ---
            W, H = 1080, 1350  # The 4:5 Tradeoff
            total_duration = 16.54
            interval_len = total_duration / 16
            photo_len = interval_len * 2
            
            # Background
            bg = ColorClip(size=(W, H), color=(0,0,0)).with_duration(total_duration)
            layers = [bg]

            for i, path in enumerate(img_paths):
                p_start = i * photo_len
                
                # Setup Image: Scale to fit 1350px height first
                clip = ImageClip(path).with_duration(photo_len).resized(height=H)
                
                # Crop width to 1080px if the photo is wider
                if clip.w > W:
                    clip = clip.cropped(x_center=clip.w/2, width=W)
                # If the photo is narrower than 1080 after resizing to H, scale to W instead
                elif clip.w < W:
                    clip = ImageClip(path).with_duration(photo_len).resized(width=W)
                    clip = clip.cropped(y_center=clip.h/2, height=H)

                # --- REVEAL LOGIC (W=1080, Center=540) ---
                # Left half: Starts at p_start
                left = (clip.cropped(x1=0, y1=0, x2=540, y2=H)
                        .with_start(p_start)
                        .with_position((0, 0)))
                
                # Right half: Starts 1 interval later
                right = (clip.cropped(x1=540, y1=0, x2=W, y2=H)
                         .with_duration(interval_len) 
                         .with_start(p_start + interval_len)
                         .with_position((540, 0)))
                
                layers.extend([left, right])

            # --- AUDIO & EXPORT ---
            audio = AudioFileClip(AUDIO_PATH).subclipped(0, total_duration)
            final_vid = CompositeVideoClip(layers, size=(W, H)).with_audio(audio)
            
            out_file = os.path.join(temp_dir, "sync_4_5.mp4")
            final_vid.write_videofile(out_file, fps=24, codec="libx264", audio_codec="aac")

            st.video(out_file)
            st.download_button("Download 4:5 Reel", open(out_file, "rb"), "potato_4_5.mp4")