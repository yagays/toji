import streamlit as st


def previous_next_button() -> None:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("< Previous"):
            st.session_state["counter"].previous()
    with col2:
        if st.button("Next >"):
            st.session_state["counter"].next()


def manuscript_view(target_text):
    st.markdown(f"# {target_text}", unsafe_allow_html=True)


def audio_player_if_exists(output_file_path):
    if output_file_path.exists():
        with output_file_path.open("rb") as f:
            audio_bytes = f.read()

        st.audio(audio_bytes)


class StatusIndicator:
    def __init__(self) -> None:
        self.box = st.empty()

    def no_frame_arrived(self):
        self.box.warning("No frame arrived.")

    def now_recording(self):
        self.box.info("Now Recording...")

    def finish_recording(self):
        self.box.success("Finish Recording")
