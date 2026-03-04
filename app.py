import streamlit as st
from moviepy import ImageClip, CompositeVideoClip, AudioFileClip, ColorClip, TextClip
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
        with st.spinner("Generate..."):
            temp_dir = tempfile.mkdtemp()
            img_paths = [os.path.join(temp_dir, f"img_{i}.jpg") for i in range(8)]
            for i, f in enumerate(uploaded_files):
                with open(img_paths[i], "wb") as out:
                    out.write(f.getvalue())

            # --- DIMENSIONS & TIMING ---
            W, H = 1080, 1350
            total_duration = 16.54
            interval_len = total_duration / 16
            photo_len = interval_len * 2
            
            layers = [ColorClip(size=(W, H), color=(0,0,0)).with_duration(total_duration)]

            for i, path in enumerate(img_paths):
                p_start = i * photo_len
                left_text_str, right_text_str = LYRICS[i]
                
                # Setup Image
                clip = ImageClip(path).with_duration(photo_len).resized(height=H)
                if clip.w > W: clip = clip.cropped(x_center=clip.w/2, width=W)

                # --- VISUAL REVEALS ---
                left_img = (clip.cropped(x1=0, y1=0, x2=540, y2=H)
                            .with_start(p_start).with_position((0, 0)))
                
                right_img = (clip.cropped(x1=540, y1=0, x2=W, y2=H)
                             .with_duration(interval_len)
                             .with_start(p_start + interval_len).with_position((540, 0)))

                # --- TEXT LAYERS ---
                # Styling to match your image: White, Sans-Serif, with a black stroke
                # --- Updated Text Function for Linux/Streamlit Compatibility ---
                def create_text(txt, start, duration, center_x):
                    return (TextClip(
                    text=txt,
                    font_size=75,
                    color='white',
                    # Use DejaVuSans-Bold for Linux compatibility
                    font='DejaVuSans-Bold', 
                    stroke_color='black',
                    stroke_width=2,
                    method='label'
            )
                .with_start(start)
                .with_duration(duration)
                # 'center' for Y, and our calculated center_x for X
                .with_position((center_x, 'center')))

# --- Updated Positioning Logic ---
# Center of Left Half (0 to 540) is 270
# Center of Right Half (540 to 1080) is 810
# Note: MoviePy positions from the TOP-LEFT of the text clip, 
# so we use 'center' in the tuple to help MoviePy handle the alignment.

                l_text = create_text(left_text_str, p_start, photo_len, 270 - 100) # Offset for width
                r_text = create_text(right_text_str, p_start + interval_len, interval_len, 810 - 100)

                layers.extend([left_img, right_img, l_text, r_text])

            # --- AUDIO & EXPORT ---
            audio = AudioFileClip(AUDIO_PATH).subclipped(0, total_duration)
            final_vid = CompositeVideoClip(layers, size=(W, H)).with_audio(audio)
            
            out_file = os.path.join(temp_dir, "final_sync.mp4")
            final_vid.write_videofile(out_file, fps=24, codec="libx264")

            st.video(out_file)
            st.download_button("Download and share it with your tomato hater.", open(out_file, "rb"), "potato_tomato_final.mp4")