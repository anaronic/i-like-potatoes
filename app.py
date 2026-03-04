import streamlit as st
from moviepy import ImageClip, CompositeVideoClip, AudioFileClip, ColorClip, TextClip
import numpy as np
import tempfile
import os
from PIL import Image

st.set_page_config(page_title="potato pohtato", page_icon="🥔", layout="medium")
st.title("🥔 Do you like potatoes?")

AUDIO_PATH = "song.mp3" 

LYRICS = [
    ("Lazy", "..."), ("Crazy", "..."), ("Scratching", "..."), ("Sports cars", "..."),
    ("I like", "potatoes"), ("I don't like", "tomatoes :("), 
    ("I'm goin'", "fishin'"), ("'Cause I'm on", "a mission")
]

# --- UI REFACTOR: UPLOADS & PREVIEWS ---
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### 📸 You alone")
    set_a = st.file_uploader("Upload 4 photos", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True, key="alone")
    
    # Pinterest-style 2x2 Grid Preview
    if set_a:
        grid_col1, grid_col2 = st.columns(2)
        for idx, img_file in enumerate(set_a):
            target_col = grid_col1 if idx % 2 == 0 else grid_col2
            with target_col:
                img = Image.open(img_file)
                st.image(img, use_container_width=True, caption=f"Photo {idx+1}")

with col_right:
    st.markdown("### 📸 You and yours")
    set_b = st.file_uploader("Upload 4 photos", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True, key="yours")
    
    # Pinterest-style 2x2 Grid Preview
    if set_b:
        grid_col1, grid_col2 = st.columns(2)
        for idx, img_file in enumerate(set_b):
            target_col = grid_col1 if idx % 2 == 0 else grid_col2
            with target_col:
                img = Image.open(img_file)
                st.image(img, use_container_width=True, caption=f"Photo {idx+5}")

st.divider()

if st.button("✨ Generate My Cute Reel", use_container_width=True):
    if len(set_a) != 4 or len(set_b) != 4:
        st.error("Please upload exactly 4 photos in BOTH sections!")
    elif not os.path.isfile(AUDIO_PATH):
        st.error(f"'{AUDIO_PATH}' not found! Ensure song.mp3 is in your GitHub repo.")
    else:
        with st.spinner("🎬 Creating your 16.54s aesthetic masterpiece..."):
            temp_dir = tempfile.mkdtemp()
            all_files = set_a + set_b
            img_paths = []
            
            for i, f in enumerate(all_files):
                path = os.path.join(temp_dir, f"img_{i}.jpg")
                with open(path, "wb") as out:
                    out.write(f.getvalue())
                img_paths.append(path)

            # --- DIMENSIONS & TIMING ---
            W, H = 1080, 1350
            HALF_W = W // 2
            TEXT_BOX_H = 150
            total_duration = 16.54
            interval_len = total_duration / 16
            photo_len = interval_len * 2
            
            layers = [ColorClip(size=(W, H), color=(0,0,0)).with_duration(total_duration)]

            def create_text(txt, start, duration, x_offset):
                return (TextClip(
                        text=txt, font_size=60, color='white', font='DejaVuSans-Bold', 
                        stroke_color='black', stroke_width=2, method='caption',
                        size=(HALF_W, TEXT_BOX_H), text_align='center'
                    )
                    .with_start(start).with_duration(duration)
                    .with_position((x_offset, 'center')))

            for i, path in enumerate(img_paths):
                p_start = i * photo_len
                l_txt, r_txt = LYRICS[i]
                
                clip = ImageClip(path).with_duration(photo_len).resized(height=H)
                if clip.w > W: clip = clip.cropped(x_center=clip.w/2, width=W)

                left_img = (clip.cropped(x1=0, y1=0, x2=HALF_W, y2=H)
                            .with_start(p_start).with_position((0, 0)))
                
                right_img = (clip.cropped(x1=HALF_W, y1=0, x2=W, y2=H)
                             .with_duration(interval_len)
                             .with_start(p_start + interval_len).with_position((HALF_W, 0)))

                layers.extend([left_img, right_img, 
                               create_text(l_txt, p_start, photo_len, 0),
                               create_text(r_txt, p_start + interval_len, interval_len, HALF_W)])

            # --- GRAINY FILTER ---
            noise = np.random.randint(0, 40, (H, W, 3), dtype='uint8')
            grain = (ImageClip(noise).with_duration(total_duration)
                     .with_opacity(0.08).with_position((0,0)))
            layers.append(grain)

            # --- EXPORT ---
            audio = AudioFileClip(AUDIO_PATH).subclipped(0, total_duration)
            final_vid = CompositeVideoClip(layers, size=(W, H)).with_audio(audio)
            
            out_file = os.path.join(temp_dir, "final_sync.mp4")
            final_vid.write_videofile(out_file, fps=24, codec="libx264", audio_codec="aac")

            st.video(out_file)
            st.download_button("Download Reel 🎬", open(out_file, "rb"), "potato_tomato_final.mp4")