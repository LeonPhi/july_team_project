import streamlit as st
from google import genai
from google.genai import types
import base64
from utils.sidebar import render_sidebar


image_path = "assets/08.jpg"
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


st.title("Bookkeeping 記帳")

client = genai.Client(
        api_key=st.secrets['Gemini']['API_KEY']
    )

config = types.GenerateContentConfig(
        system_instruction=""
    )










render_sidebar()