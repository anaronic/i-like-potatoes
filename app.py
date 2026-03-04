import streamlit as st
from moviepy import ImageClip, CompositeVideoClip, AudioFileClip, ColorClip
import tempfile
import os

st.title("🥔")

uploaded_files = st.file_uploader("Upload 8 Photos (in order)", type=['jpg', 'png'], accept_multiple_files=True)
audio_file = os.path.join(os.getcwd(), "song.mp3")

if st.button("Generate") and len(uploaded_files) == 8 and audio_file:
    with st.spinner("Syncing 8 photos to the beat..."):
        # Save files to temp
        temp_dir = tempfile.mkdtemp()
        img_paths = [os.path.join(temp_dir, f"img_{i}.jpg") for i in range(8)]
        for i, f in enumerate(uploaded_files):
            with open(img_paths[i], "wb") as out:
                out.write(f.getvalue())
        
        audio_path = os.path.join(temp_dir, "audio.mp3")
        with open(audio_path, "wb") as f:
            f.write(audio_file.getvalue())

        # Logic
        beat_duration = 0.75  # The 'pulse' of the song
        layers = [ColorClip(size=(1080, 1920), color=(0,0,0)).set_duration(beat_duration * 8)]

        for i, path in enumerate(img_paths):
            start_time = i * beat_duration
            
            # Prepare image (9:16 ratio)
            clip = ImageClip(path).resize(height=1920).set_duration(beat_duration)
            if clip.w > 1080:
                clip = clip.crop(x_center=clip.w/2, width=1080)

            # --- THE REVEAL ---
            # 1. Left half appears at the start of the beat
            left = clip.crop(x1=0, y1=0, x2=540, y2=1920).set_start(start_time).set_position((0,0))
            
            # 2. Right half appears halfway through the beat (approx 0.37s later)
            right_offset = beat_duration * 0.4 
            right = clip.crop(x1=540, y1=0, x2=1080, y2=1920).set_start(start_time + right_offset).set_position((540,0))
            
            layers.extend([left, right])

        # Render
        final_audio = AudioFileClip(audio_path).subclip(0, beat_duration * 8)
        final_vid = CompositeVideoClip(layers, size=(1080, 1920)).set_audio(final_audio)
        
        out_file = os.path.join(temp_dir, "reel.mp4")
        final_vid.write_videofile(out_file, fps=24, codec="libx264")

        st.video(out_file)
        st.download_button("Download", open(out_file, "rb"), "potato_edit.mp4")