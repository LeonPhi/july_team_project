import streamlit as st
from utils.sidebar import render_sidebar

st.toast(f"👋 嗨, {st.session_state.username}!")

if st.button("Recipe 食譜推薦"):
    st.switch_page("pages/recipe.py")

if st.button("Accounting 記帳"):
    st.switch_page("pages/accounting.py")

if st.button("Music 音樂"):
    st.switch_page("pages/music.py")

if st.button("Greeting Card 賀卡"):
    st.switch_page("pages/card.py")

render_sidebar()