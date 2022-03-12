import hashlib
import queue
import shutil
from pathlib import Path

import pydub
import streamlit as st
from streamlit_webrtc import WebRtcMode, webrtc_streamer

import toji.ui.main as ui_main
import toji.ui.sidebar as ui_sidebar
from toji.config import TojiSettings
from toji.util import Counter

settings = TojiSettings()


def main():
    # initialize
    if "counter" not in st.session_state:
        st.session_state["counter"] = Counter()
    if "records" not in st.session_state:
        st.session_state["records"] = {}

        # initialize wav dir
        if settings.wav_dir_path.exists():
            shutil.rmtree(str(settings.wav_dir_path))
        settings.wav_dir_path.mkdir()

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
        output_file_path = settings.wav_dir_path / output_file_name
        record_info = {"text": target_text, "file_name": output_file_name}

        ui_main.manuscript_view(target_text)
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

        status_indicator = ui_main.StatusIndicator()

        while True:
            if webrtc_ctx.audio_receiver:
                try:
                    audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
                except queue.Empty:
                    status_indicator.no_frame_arrived()
                    continue

                status_indicator.now_recording()

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
            status_indicator.finish_recording()
            try:
                st.session_state["records"][output_file_name] = record_info
                audio_buffer.export(str(output_file_path), format="wav")
            except BaseException:
                st.error("Error while Writing wav to disk")

            # Reset
            st.session_state["audio_buffer"] = pydub.AudioSegment.empty()

        ui_main.audio_player_if_exists(output_file_path)

    if ui_sidebar.has_at_least_one_wav_file():
        ui_sidebar.progress_bar_and_stats()
        ui_sidebar.proceed_to_download(settings)


if __name__ == "__main__":
    main()
