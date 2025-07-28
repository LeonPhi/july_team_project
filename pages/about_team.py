import streamlit as st
import base64
from utils.sidebar import render_sidebar

#from forms.contact import contact_form


#@st.experimental_dialog("Contact Me")
#def show_contact_form():
#    contact_form()


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


# --- HERO SECTION ---
col1, col2 = st.columns(2, gap="small", vertical_alignment="center")
with col1:
    st.image("./assets/logo.png", width=230)

with col2:
    st.title("長者生活通", anchor=False)
#    if st.button("✉️ Contact Me"):
#        show_contact_form()


# --- EXPERIENCE & QUALIFICATIONS ---
st.write("\n")
st.write(r"$\textsf{結合語音、圖像與情緒辨識等 AI 技術的長者智慧生活 App，}$")
st.write(r"$\textsf{致力於用科技陪伴並協助長者更安心、便利地過每一天。}$")
st.subheader("Team Members", anchor=False)
st.write(
    """
    - 張揚恩
    - 沈柏昱
    - 胡華容
    - 杜羽喬
    - 楊尹軒
    """
)

# --- SKILLS ---
#st.write("\n")
#st.subheader("Skills", anchor=False)
#st.write(
#    """
#    - 12345678
#    - 12345678
#    - 12345678
#    """
#)

render_sidebar()