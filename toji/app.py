import shutil

import streamlit as st

import toji.ui.main as ui_main
import toji.ui.sidebar as ui_sidebar
from toji.config import TojiSettings
from toji.record import Record, RecordStrage
from toji.util import Counter
from toji.webrtc import WebRTCRecord

settings = TojiSettings()


def initialize_startup():
    # Initialize
    if "counter" not in st.session_state:
        st.session_state["counter"] = Counter()
    if "records" not in st.session_state:
        st.session_state["records"] = RecordStrage()

        # initialize wav dir
        if settings.wav_dir_path.exists():
            shutil.rmtree(str(settings.wav_dir_path))
        settings.wav_dir_path.mkdir()


def main():
    initialize_startup()

    # To redraw the entire window, this should be declared first.
    ui_main.previous_next_button()

    # Siebar
    ui_sidebar.title()
    ui_sidebar.manuscripts_text_area()
    if ui_sidebar.has_at_least_one_wav_file():
        ui_sidebar.progress_bar_and_stats()
        ui_sidebar.proceed_to_download(settings)

    # Main Window (only visible when manuscript is in the text area)
    if st.session_state["manuscripts"]:
        texts = [t for t in st.session_state["manuscripts"].split("\n") if t]
        if st.session_state["counter"].total is None:
            st.session_state["counter"].set_total(len(texts))

        record = Record(
            manuscript_index=st.session_state["counter"].index,
            text=texts[st.session_state["counter"].index],
            wav_dir_path=settings.wav_dir_path,
        )

        ui_main.manuscript_view(record.text)

        webrtc_record = WebRTCRecord()
        webrtc_record.recording(record)

        ui_main.audio_player_if_exists(record.wav_file_path)


if __name__ == "__main__":
    main()
