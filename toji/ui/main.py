import streamlit as st


def previous_next_button() -> None:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("< Previous"):
            st.session_state["counter"].previous()
    with col2:
        if st.button("Next >"):
            st.session_state["counter"].next()
