import hashlib
import json
import queue
import shutil
import zipfile
from pathlib import Path

import pydub
import streamlit as st
from streamlit_webrtc import WebRtcMode, webrtc_streamer

from toji.util import Counter


def main():
    wav_dir = Path("data/")
    record_info_path = wav_dir / "meta.json"
    archive_filename = "toji_wav_archive.zip"

    # initialize
    if "counter" not in st.session_state:
        st.session_state["counter"] = Counter()
    if "records" not in st.session_state:
        st.session_state["records"] = []

        # initialize wav dir
        shutil.rmtree(str(wav_dir))
        wav_dir.mkdir(exist_ok=True)

    st.sidebar.title("Toji - Voice Recorder")
    all_text = st.sidebar.text_area("input texts", "")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("previous"):
            st.session_state["counter"].previous()
    with col2:
        if st.button("next"):
            st.session_state["counter"].next()

    if all_text:
        texts = [t for t in all_text.split("\n") if t]

        if st.session_state["counter"].total is None:
            st.session_state["counter"].set_total(len(texts))

        target_index = st.session_state["counter"].index
        target_text = texts[target_index]
        file_id = hashlib.md5((target_text + str(target_index)).encode()).hexdigest()
        output_file_name = f"{file_id}.wav"
        output_file_path = wav_dir / output_file_name
        record_info = {"text": target_text, "file_name": output_file_name}

        st.title(f"{target_text}")
        webrtc_ctx = webrtc_streamer(
            key="sendonly-audio",
            mode=WebRtcMode.SENDONLY,
            audio_receiver_size=256,
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
            media_stream_constraints={
                "audio": True,
            },
        )

        if "audio_buffer" not in st.session_state:
            st.session_state["audio_buffer"] = pydub.AudioSegment.empty()

        status_indicator = st.empty()

        while True:
            if webrtc_ctx.audio_receiver:
                try:
                    audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
                except queue.Empty:
                    status_indicator.warning("No frame arrived.")
                    continue

                status_indicator.info("Now Recording...")

                sound_chunk = pydub.AudioSegment.empty()
                for audio_frame in audio_frames:
                    sound = pydub.AudioSegment(
                        data=audio_frame.to_ndarray().tobytes(),
                        sample_width=audio_frame.format.bytes,
                        frame_rate=audio_frame.sample_rate,
                        channels=len(audio_frame.layout.channels),
                    )
                    sound_chunk += sound

                if len(sound_chunk) > 0:
                    st.session_state["audio_buffer"] += sound_chunk
            else:
                break

        audio_buffer = st.session_state["audio_buffer"]

        if not webrtc_ctx.state.playing and len(audio_buffer) > 0:
            status_indicator.success("Finish Recording")
            try:
                st.session_state["records"].append(record_info)
                audio_buffer.export(str(output_file_path), format="wav")
            except BaseException:
                st.error("Error while Writing wav to disk")

            # Reset
            st.session_state["audio_buffer"] = pydub.AudioSegment.empty()

        if output_file_path.exists():
            with output_file_path.open("rb") as f:
                audio_bytes = f.read()

            st.audio(audio_bytes)

    if st.session_state["counter"].total:
        # progress bar
        st.sidebar.subheader("Stats")
        progress_percent = st.session_state["counter"].progress_percent if st.session_state["counter"].total else 0.0
        st.sidebar.progress(progress_percent)

        # stats
        current_num = st.session_state["counter"].index + 1
        total_num = st.session_state["counter"].total if st.session_state["counter"].total else 0
        st.sidebar.write(f"{current_num} / {total_num}")

        # download
        if st.sidebar.button("Proceed to download"):
            n_files = 0
            with record_info_path.open("w") as f:
                json.dump(st.session_state["records"], f, ensure_ascii=False, indent=4)
            with zipfile.ZipFile(archive_filename, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
                for file_path in wav_dir.rglob("*"):
                    archive.write(file_path, arcname=file_path.relative_to(wav_dir))
                    n_files += 1
            st.sidebar.write("Archive Stats:")
            st.sidebar.write(f"- Num. of wav files {n_files -1 }")  # -1 for meta.json
            with open(archive_filename, "rb") as fp:
                st.sidebar.download_button(
                    label="Download", data=fp, file_name=archive_filename, mime="application/zip"
                )


if __name__ == "__main__":
    main()
