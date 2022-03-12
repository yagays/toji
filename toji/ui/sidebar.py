import json
import zipfile

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
        n_files = 0
        with settings.record_info_path.open("w") as f:
            json.dump(
                [record_info for _, record_info in st.session_state["records"].items()],
                f,
                ensure_ascii=False,
                indent=4,
            )
        with zipfile.ZipFile(settings.archive_filename, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for file_path in settings.wav_dir_path.rglob("*"):
                archive.write(file_path, arcname=file_path.relative_to(settings.wav_dir_path))
                n_files += 1
        st.sidebar.write("Archive Stats:")
        st.sidebar.write(f"- Num. of wav files {n_files -1 }")  # -1 for meta.json
        with open(settings.archive_filename, "rb") as fp:
            st.sidebar.download_button(
                label="Download", data=fp, file_name=settings.archive_filename, mime="application/zip"
            )
