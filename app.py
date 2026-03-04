import streamlit as st
from moviepy import ImageClip, CompositeVideoClip, AudioFileClip, ColorClip, TextClip
import numpy as np
import tempfile
import os

st.set_page_config(page_title="potato pohtato", page_icon="🥔")
st.title("🥔 Do you like potatoes?")

AUDIO_PATH = "song.mp3" 

LYRICS = [
    ("Lazy", "..."),
    ("Crazy", "..."),
    ("Scratching", "..."),
    ("Sports cars", "..."),
    ("I like", "potatoes"),
    ("I don't like", "tomatoes :("),
    ("I'm goin'", "fishin'"),
    ("'Cause I'm on", "a mission")
]

uploaded_files = st.file_uploader("Upload 8 Photos", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

if st.button("Generate a cute reel"):
    if len(uploaded_files) != 8:
        st.error("Please upload exactly 8 photos!")
    elif not os.path.isfile(AUDIO_PATH):
        st.error(f"'{AUDIO_PATH}' not found in GitHub!")
    else:
        with st.spinner("Generating..."):
            temp_dir = tempfile.mkdtemp()
            img_paths = [os.path.join(temp_dir, f"img_{i}.jpg") for i in range(8)]
            for i, f in enumerate(uploaded_files):
                with open(img_paths[i], "wb") as out:
                    out.write(f.getvalue())

            # --- DIMENSIONS & TIMING ---
            W, H = 1080, 1350
            HALF_W = W // 2 # 540
            TEXT_BOX_H = 200 # Fixed height for the text container to prevent chopping
            total_duration = 16.54
            interval_len = total_duration / 16
            photo_len = interval_len * 2
            
            layers = [ColorClip(size=(W, H), color=(0,0,0)).with_duration(total_duration)]

            # --- REFINED TEXT FUNCTION ---
            def create_text(txt, start, duration, x_offset):
                return (TextClip(
                        text=txt,
                        font_size=80,
                        color='white',
                        font='DejaVuSans-Bold', 
                        stroke_color='black',
                        stroke_width=2,
                        method='caption', # Caption is better for centering without chopping
                        size=(HALF_W, TEXT_BOX_H), # Set a defined box
                        text_align='center' # Align horizontally inside box
                    )
                    .with_start(start)
                    .with_duration(duration)
                    # Vertical 'center' for the box itself
                    .with_position((x_offset, 'center')))

            for i, path in enumerate(img_paths):
                p_start = i * photo_len
                left_text_str, right_text_str = LYRICS[i]
                
                # Setup Image
                clip = ImageClip(path).with_duration(photo_len).resized(height=H)
                if clip.w > W: 
                    clip = clip.cropped(x_center=clip.w/2, width=W)

                # --- VISUAL REVEALS ---
                left_img = (clip.cropped(x1=0, y1=0, x2=HALF_W, y2=H)
                            .with_start(p_start).with_position((0, 0)))
                
                right_img = (clip.cropped(x1=HALF_W, y1=0, x2=W, y2=H)
                             .with_duration(interval_len)
                             .with_start(p_start + interval_len).with_position((HALF_W, 0)))

                # --- CENTERED TEXT LAYERS ---
                l_text = create_text(left_text_str, p_start, photo_len, 0)
                r_text = create_text(right_text_str, p_start + interval_len, interval_len, HALF_W)

                layers.extend([left_img, right_img, l_text, r_text])

            # --- GRAINY FILTER ---
            noise = np.random.randint(0, 40, (H, W, 3), dtype='uint8')
            grain = (ImageClip(noise).with_duration(total_duration)
                     .with_opacity(0.08).with_position((0,0)))
            layers.append(grain)

            # --- AUDIO & EXPORT ---
            audio = AudioFileClip(AUDIO_PATH).subclipped(0, total_duration)
            final_vid = CompositeVideoClip(layers, size=(W, H)).with_audio(audio)
            
            out_file = os.path.join(temp_dir, "final_sync.mp4")
            final_vid.write_videofile(out_file, fps=24, codec="libx264", audio_codec="aac")

            st.video(out_file)
            st.download_button("Download Reel", open(out_file, "rb"), "potato_tomato_final.mp4")