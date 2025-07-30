import streamlit as st
from google import genai
from google.genai import types
import base64
import pandas as pd
import json
import datetime
from streamlit_gsheets import GSheetsConnection
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

if "already_submit" not in st.session_state:
    st.session_state.already_submit = False

conn = st.connection("gsheets", type=GSheetsConnection)

client = genai.Client(
        api_key=st.secrets['Gemini']['API_KEY']
    )

today = str(datetime.date.today())

prompt_receipt="""
Given the receipt image provided, extract all relevant information and structure the output 
as detailed JSON that matches the database schema for storing receipt data. 

The receipt data should include: 
date (Format: yyyy-mm-dd), 
type (Choose type from: 餐飲/交通/住房/娛樂/購物/醫療保健/禮品/其他), 
total price (Change all currency to NTD. *Add all individual prices and compare to total to verify in case of unclear text*) 
and short description of the transaction.

Exclude any sensitive information from the output. **Please input with Traditional Chinese.**
Today is """ + today + """.
Format the JSON as follows:

{
  "receipt_data": {
    "date": "",
    "type": "",
    "total": 0,
    "description": ""
  }
}

Example:

{
  "receipt_data": {
    "date": "2025-07-01",
    "type": "購物",
    "total": 225,
    "description": "清潔工具"
  }
}

"""

config_text=types.GenerateContentConfig(
    system_instruction="""
Given the user's input, extract all relevant information and structure the output 
as detailed JSON that matches the database schema for storing receipt data. 

The receipt data should include: 
date (Format: yyyy-mm-dd), 
type (Choose type from: 餐飲/交通/住房/娛樂/購物/醫療保健/禮品/其他), 
total price (Change all currency to NTD. *Add all individual prices and compare to total to verify in case of unclear text*) 
and short description of the transaction.

Exclude any sensitive information from the output. **Please input with Traditional Chinese.**
Today is """ + today + """.
Format the JSON as follows:

{
  "receipt_data": {
    "date": "",
    "type": "",
    "total": 0,
    "description": ""
  }
}

Example:

{
  "receipt_data": {
    "date": "2025-07-01",
    "type": "購物",
    "total": 225,
    "description": "清潔工具"
  }
}

"""

)


username = st.session_state.username

def get_receipt_data(json_string):
    if "receipt_data" not in st.session_state:
        clean_json_string = json_string.strip('`').replace('json\n', '')
        st.session_state.receipt_data = json.loads(clean_json_string)["receipt_data"]

    receipt_data = st.session_state.receipt_data
    type_list = ["餐飲","交通","住房","娛樂","購物","醫療保健","禮品","其他"]
    type_list.insert(0, type_list.pop(type_list.index(receipt_data["type"])))

    with st.form('明細資料'):
        expense_date = st.date_input(r"$\textsf{\Large 日期 (YYYY-MM-DD)}$", receipt_data["date"])
        expense_type = st.selectbox(r"$\textsf{\Large 類別}$", type_list)
        expense_total = st.text_input(r"$\textsf{\Large 金額 (NTD)}$", str(receipt_data["total"]))
        description = st.text_input(r"$\textsf{\Large 說明}$", receipt_data["description"])
        submit = st.form_submit_button("Submit 提交")
    
    if submit and all([expense_date, expense_type, expense_total, description]):
        st.session_state.submitted_data = {
            "date": str(expense_date),
            "type": expense_type,
            "total": expense_total,
            "description": description
        }
        st.rerun()

    elif not all([expense_date, expense_type, expense_total, description]):
        st.warning("⚠️ Please fill out all fields before submitting.")


use_photo = st.toggle(r"$\textsf{\Large 使用交易明細照片(多語言)}$", value=True)
if use_photo:

    use_camera = st.toggle(r"$\textsf{\Large 使用拍照功能}$", value=True)
    if use_camera:
        photo = st.camera_input(r"$\textsf{\Large 請拍交易明細照片}$")
        if photo:
            photo = photo.getvalue()

    else:
        photo = st.file_uploader(r"$\textsf{\Large 請上傳交易明細照片}$", \
            type=["png", "jpeg", "jpg", "webp", "avif"])
        if photo:
            photo = photo.read()
            st.image(photo, caption='Receipt 交易明細')

    if photo:
        if st.button('分析交易明細'):
            with st.spinner('請稍等...'):
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        prompt_receipt,
                        types.Part.from_bytes(data=photo,mime_type='image/jpeg')
                    ]
                )
                st.session_state.json_string = response.text

else:
    user_input = st.text_input(r'$\textsf{請輸入消費資料}$', key=1)
    if user_input:
        if st.button('分析文字'):
            with st.spinner('請稍等...'):
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[user_input,],
                    config=config_text
                )
                st.session_state.json_string = response.text


if "json_string" in st.session_state and "submitted_data" not in st.session_state:
    data = get_receipt_data(st.session_state.json_string)

if "submitted_data" in st.session_state and not st.session_state.already_submit:

    entry = pd.DataFrame([{
        "username": st.session_state.username,
        **st.session_state.submitted_data
    }])

    existing_data = conn.read(worksheet="Expenses", usecols=list(range(5)), ttl=5)
    safe_existing = existing_data.drop(columns=["password", "email", "photo_path"], errors="ignore")


    updated_data = pd.concat([safe_existing, entry], ignore_index=True)


    conn.update(worksheet="Expenses", data=updated_data)
    st.session_state.already_submit = True

if st.session_state.already_submit: 
    st.success("🎉 提交的資料:")
    st.json(st.session_state.submitted_data)
    if st.button("提交新資料"):
        del st.session_state.receipt_data
        del st.session_state.json_string
        del st.session_state.submitted_data
        del st.session_state.already_submit
        st.rerun()


render_sidebar()