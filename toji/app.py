import hashlib
import queue
import shutil
from pathlib import Path

import pydub
import streamlit as st
from streamlit_webrtc import WebRtcMode, webrtc_streamer

import toji.ui.main as ui_main
import toji.ui.sidebar as ui_sidebar
from toji.util import Counter


def main():
    wav_dir = Path("data/")
    record_info_path = wav_dir / "meta.json"
    archive_filename = "toji_wav_archive.zip"

    # initialize
    if "counter" not in st.session_state:
        st.session_state["counter"] = Counter()
    if "records" not in st.session_state:
        st.session_state["records"] = {}

        # initialize wav dir
        if wav_dir.exists():
            shutil.rmtree(str(wav_dir))
        wav_dir.mkdir()

    ui_sidebar.title()
    ui_sidebar.manuscripts_text_area()
    ui_main.previous_next_button()

    if st.session_state["manuscripts"]:
        texts = [t for t in st.session_state["manuscripts"].split("\n") if t]

        if st.session_state["counter"].total is None:
            st.session_state["counter"].set_total(len(texts))

        target_index = st.session_state["counter"].index
        target_text = texts[target_index]
        file_id = hashlib.md5((target_text + str(target_index)).encode()).hexdigest()
        output_file_name = f"{file_id}.wav"
        output_file_path = wav_dir / output_file_name
        record_info = {"text": target_text, "file_name": output_file_name}

        st.markdown(f"# {target_text}", unsafe_allow_html=True)
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
                st.session_state["records"][output_file_name] = record_info
                audio_buffer.export(str(output_file_path), format="wav")
            except BaseException:
                st.error("Error while Writing wav to disk")

            # Reset
            st.session_state["audio_buffer"] = pydub.AudioSegment.empty()

        if output_file_path.exists():
            with output_file_path.open("rb") as f:
                audio_bytes = f.read()

            st.audio(audio_bytes)

    if ui_sidebar.has_at_least_one_wav_file():
        ui_sidebar.progress_bar_and_stats()
        ui_sidebar.proceed_to_download(record_info_path, archive_filename, wav_dir)


if __name__ == "__main__":
    main()
