import streamlit as st


def title() -> None:
    st.sidebar.title("toji - Voice Recorder")


def manuscripts_text_area() -> None:
    st.sidebar.text_area("input texts", "", key="manuscripts")


def progress_bar_and_stats() -> None:
    st.sidebar.subheader("Progress")
    progress_percent = st.session_state["counter"].progress_percent if st.session_state["counter"].total else 0.0
    st.sidebar.progress(progress_percent)

    # Stats like `2/10`
    current_num = st.session_state["counter"].index + 1
    total_num = st.session_state["counter"].total if st.session_state["counter"].total else 0
    st.sidebar.write(f"{current_num} / {total_num}")


def has_at_least_one_wav_file():
    return st.session_state["counter"].total


def proceed_to_download(settings):
    if st.sidebar.button("Proceed to download"):
        st.session_state["records"].export_record_info_as_json(settings.record_info_path)
        st.session_state["records"].compress_wav_files_into_zip(settings.archive_filename, settings.wav_dir_path)
        num_wav_files = st.session_state["records"].num_wav_files

        st.sidebar.write("Archive Stats:")
        st.sidebar.write(f"- Num. of wav files {num_wav_files}")
        with open(settings.archive_filename, "rb") as fp:
            st.sidebar.download_button(
                label="Download", data=fp, file_name=settings.archive_filename, mime="application/zip"
            )
