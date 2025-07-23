import streamlit as st

def render_sidebar():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        st.sidebar.markdown(f"👋 Hello, {st.session_state.username}")
        if st.sidebar.button("🚪 Log Out"):
            st.session_state.logged_in = False
            st.rerun()