import streamlit as st
from google import genai
import base64
from google.genai import types
from utils.sidebar import render_sidebar


image_path = "assets/07_fix.jpg"
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


key = st.secrets['Gemini']['API_KEY']
client = genai.Client(
        api_key=key,
)

st.title('Identify Item 物品辨識')

lang = st.text_input(r"$\textsf{\Large Language:}$")

st.write('\n')
st.write('\n')

use_camera = st.toggle(r"$\textsf{拍照輸入照片}$", value=True)
if use_camera:
    photo = st.camera_input(r"$\textsf{\Large 拍物品照片 (圖片內可以有多樣物品)}$")
    if photo:
        photo = photo.getvalue()
else:
    photo = st.file_uploader(r"$\textsf{\Large 請上傳物品照片 (圖片內可以有多樣物品)}$", \
                type=["png", "jpeg", "jpg", "webp", "avif"])
    if photo:
        photo = photo.read()
        st.image(photo, caption='Image 圖片')

prompt = f"""
Please help me:
1. Explain what the item in the photo is
2. Please use "{lang}" for the language of your answer (if "" empty, use Traditional Chinese)
"""

if photo and st.button('辨識物品'):
    with st.spinner('請稍等...'):
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                prompt,
                types.Part.from_bytes(
                    data=photo,
                    mime_type='image/jpeg',
                )
            ]
        )
        st.text_area('AI', response.text, height=400)


render_sidebar()