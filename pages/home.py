import streamlit as st
import base64
from utils.sidebar import render_sidebar


image_path = "assets/01.jpg"
with open(image_path, "rb") as img_file:
    base64_image = base64.b64encode(img_file.read()).decode()

page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpg;base64,{base64_image}");
        background-size: cover;
        background-position: center;
    }}
    [data-testid="stHeader"] {{
        background-color: rgba(0,0,0,0);
    }}
    </style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)


st.toast(f"👋 嗨, {st.session_state.username}!")

if st.button("Recipe 食譜推薦"):
    st.switch_page("pages/recipe.py")

if st.button("Bookkeeping 記帳"):
    st.switch_page("pages/expense.py")

if st.button("Identify Item 物品辨識"):
    st.switch_page("pages/expense.py")

if st.button("Music 音樂"):
    st.switch_page("pages/music.py")

if st.button("Greeting Card 賀卡"):
    st.switch_page("pages/card.py")

render_sidebar()