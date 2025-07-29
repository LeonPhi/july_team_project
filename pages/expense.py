import streamlit as st
from google import genai
from google.genai import types
import base64
import datetime
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


st.title("Bookkeeping 記帳 (尚未完成)")

client = genai.Client(
        api_key=st.secrets['Gemini']['API_KEY']
    )

today = str(datetime.date.today())

prompt_receipt="""
Given the receipt image provided, extract all relevant information and structure the output 
as detailed JSON that matches the database schema for storing receipt data. 
The receipt data should include date, type (always expense), items, 
total price of every type of item and complete total price on the receipt. 
Exclude any sensitive information from the output. *Please input with Traditional Chinese.*
Today is """ + today + """.
Format the JSON as follows:

{
  "receipt_data": {
    "date": "",
    "type": "expense",
    "items": [
      {
        "": 0,
        "": 0,
        "": 0,
        (And so on)
      }
    ],
    "total": 0,
}

Example:
{
  "receipt_data": {
    "date": "2025/07/01 13:20",
    "type": "expense",
    "items": [
      {
        "蘋果": 20,
        "香蕉": 30,
        "掃把": 40,
        "肥皂": 35
      }
    ],
    "total": 125,
}
"""

config_text=types.GenerateContentConfig(
    system_instruction="""
Given the user's input, extract all relevant information and structure the output 
as detailed JSON that matches the database schema for storing receipt data. 
The receipt data should include date, type (always expense), items, 
total price of every type of item and complete total price on the receipt. 
Exclude any sensitive information from the output. *Please input with Traditional Chinese.*
Today is """ + today + """.
Format the JSON as follows:

{
  "receipt_data": {
    "date": "",
    "type": "expense",
    "items": [
      {
        "": 0,
        "": 0,
        "": 0,
        (And so on)
      }
    ],
    "total": 0,
}

Example:

{
  "receipt_data": {
    "date": "2025/07/01 13:20",
    "type": "expense",
    "items": [
      {
        "蘋果": 20,
        "香蕉": 30,
        "掃把": 40,
        "肥皂": 35
      }
    ],
    "total": 125,
}

"""

)

use_photo = st.toggle(r"$\textsf{\Large 使用發票照片}$", value=True)
if use_photo:

    use_camera = st.toggle(r"$\textsf{\Large 使用拍照功能}$", value=True)
    if use_camera:
        photo = st.camera_input(r"$\textsf{\Large 請拍發票照片}$")
        if photo:
            photo = photo.getvalue()

    else:
        photo = st.file_uploader(r"$\textsf{\Large 請上傳發票照片}$", \
            type=["png", "jpeg", "jpg", "webp", "avif"])
        if photo:
            photo = photo.read()
            st.image(photo, caption='Receipt 發票')

    if photo:
        if st.button('分析發票'):
            with st.spinner('請稍等...'):
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        prompt_receipt,
                        types.Part.from_bytes(
                            data=photo,
                            mime_type='image/jpeg',
                        )
                    ]
                )
                st.text_area('AI', response.text, height=400)

else:
    user_input = st.text_input(r'$\textsf{請輸入消費資料}$', key=1)
    if user_input:
        if st.button('分析文字'):
            with st.spinner('請稍等...'):
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        user_input,
                    ],
                    config=config_text
                )
                st.text_area('AI', response.text, height=400)


render_sidebar()
