import streamlit as st
from moviepy import ImageClip, CompositeVideoClip, AudioFileClip, ColorClip, TextClip
import numpy as np
import tempfile
import os
from PIL import Image

# --- CONFIG & TITLES ---
st.set_page_config(page_title="potato pohtato", page_icon="🥔")
st.title("🥔 Do you like potatoes?")

AUDIO_PATH = "song.mp3" 

LYRICS = [
    ("Lazy", "..."), ("Crazy", "..."), ("Scratching", "..."), ("Sports cars", "..."),
    ("I like", "potatoes"), ("I don't like", "tomatoes :("), 
    ("I'm goin'", "fishin'"), ("'Cause I'm on", "a mission")
]

# --- CSS TO HIDE THE MESSY FILENAMES AND CROSS BUTTONS ---
st.markdown("""
    <style>
    /* Hides the default Streamlit file list (hex names, sizes, and 'X') */
    [data-testid="stFileUploaderFileList"] {
        display: none !important;
    }
    /* Tightens the gap between the uploader and your custom grid */
    .stFileUploader {
        margin-bottom: -10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDE-BY-SIDE INPUTS ---
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### 📸 You alone")
    set_a = st.file_uploader("Upload 4 photos", type=['jpg', 'jpeg', 'png'], 
                             accept_multiple_files=True, key="alone", 
                             label_visibility="collapsed")
    if set_a:
        # Displaying custom "Photo X" labels in a 1x4 row
        cols = st.columns(4)
        for idx, img_file in enumerate(set_a):
            with cols[idx]:
                st.image(Image.open(img_file), use_container_width=True)
                st.caption(f"Photo {idx+1}")

with col_right:
    st.markdown("### 📸 You and yours")
    set_b = st.file_uploader("Upload 4 photos", type=['jpg', 'jpeg', 'png'], 
                             accept_multiple_files=True, key="yours", 
                             label_visibility="collapsed")
    if set_b:
        # Displaying custom "Photo X" labels in a 1x4 row
        cols = st.columns(4)
        for idx, img_file in enumerate(set_b):
            with cols[idx]:
                st.image(Image.open(img_file), use_container_width=True)
                st.caption(f"Photo {idx+5}")

st.divider()

# --- GENERATION LOGIC ---
if st.button("✨ Generate My Nostalgic Reel", use_container_width=True):
    if len(set_a) != 4 or len(set_b) != 4:
        st.error("Please upload exactly 4 photos in BOTH sections!")
    elif not os.path.isfile(AUDIO_PATH):
        st.error(f"'{AUDIO_PATH}' not found!")
    else:
        with st.spinner("🎞️ Adding heavy grain and vignette glow..."):
            temp_dir = tempfile.mkdtemp()
            all_files = set_a + set_b
            img_paths = [os.path.join(temp_dir, f"img_{i}.jpg") for i in range(8)]
            for i, f in enumerate(all_files):
                with open(img_paths[i], "wb") as out:
                    out.write(f.getvalue())

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

            # --- NOSTALGIC EFFECTS ---
            # 1. HEAVIER GRAIN
            noise = np.random.randint(0, 55, (H, W, 3), dtype='uint8')
            grain = (ImageClip(noise).with_duration(total_duration)
                     .with_opacity(0.15).with_position((0,0)))
            
            # 2. VIGNETTE GLOW
            x = np.linspace(-1, 1, W)
            y = np.linspace(-1, 1, H)
            X, Y = np.meshgrid(x, y)
            vignette_data = np.sqrt(X**2 + Y**2)
            vignette_data = (vignette_data / vignette_data.max()) * 255
            vignette_mask = np.stack([vignette_data]*3, axis=-1).astype('uint8')
            
            glow_vignette = (ImageClip(vignette_mask)
                             .with_duration(total_duration)
                             .with_opacity(0.25)
                             .with_position((0,0)))

            layers.extend([glow_vignette, grain])

            # --- EXPORT ---
            audio = AudioFileClip(AUDIO_PATH).subclipped(0, total_duration)
            final_vid = CompositeVideoClip(layers, size=(W, H)).with_audio(audio)
            
            out_file = os.path.join(temp_dir, "final_sync.mp4")
            final_vid.write_videofile(out_file, fps=24, codec="libx264", audio_codec="aac")

            st.video(out_file)
            st.download_button("Download My Masterpiece 🎬", open(out_file, "rb"), "potato_nostalgia_final.mp4")