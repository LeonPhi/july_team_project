import streamlit as st
from PIL import Image, UnidentifiedImageError
import numpy as np
import face_recognition
import base64
import os
from streamlit_gsheets import GSheetsConnection
import bcrypt

conn = st.connection('gsheets', type=GSheetsConnection)

# Enlarged gradient heading
st.markdown("""
<style>
/* Glowy title text */
.gradient-text {
    background: linear-gradient(to right, #ff6a00, #ee0979);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 4rem;
    font-weight: 900;
    text-align: center;
    margin-bottom: 2rem;
}
            
.title-text {
    font-size: 3rem;
    font-weight: 700;   
    text-align: center;       
}

/* Enlarge toggle label */
div[data-testid="stToggle"] > label {
    font-size: 4rem !important;
    font-weight: 800 !important;
}

/* Enlarge switch itself */
div[data-testid="stToggle"] .st-d5 {
    transform: scale(2.2);
}
.stMarkdown p, .stMarkdown ul, .stMarkdown ol { font-size: 1.5rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-text">DailyGenie 生活通</div>', unsafe_allow_html=True)
st.markdown('<div class="gradient-text">Login 登入</div>', unsafe_allow_html=True)

# Function to encode image to base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    return encoded

# Background Images
image_path_1 = "assets/04_fix1.jpg"
image_path_2 = "assets/04_fix.jpg"
base64_image_1 = get_base64_image(image_path_1)
base64_image_2 = get_base64_image(image_path_2)

# Toggle-based login switch
use_face_login = st.toggle(r"$\textsf{\Large Use Face Login}$", value=True)

# Initialize session state
if "theme" not in st.session_state:
    st.session_state.theme = "1"

# Change theme based on toggle state
if use_face_login:
    st.session_state.theme = "2"  # dark
else:
    st.session_state.theme = "1"  # light

# Function to apply theme
def change_theme_bg(theme):
    if theme == "1":
        page_bg_img = f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/jpg;base64,{base64_image_1}");
            background-size: cover;
            background-position: center;
        }}
        [data-testid="stHeader"] {{
            background-color: rgba(0,0,0,0);
        }}
        </style>
        """
    else:
        page_bg_img = f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/jpg;base64,{base64_image_2}");
            background-size: cover;
            background-position: center;
        }}
        [data-testid="stHeader"] {{
            background-color: rgba(0,0,0,0);
        }}
        </style>
        """
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Apply selected theme
change_theme_bg(st.session_state.theme)

# Connect to database
def verify_credentials(username, password):
    existing_users = conn.read(worksheet="Users", usecols=list(range(4)), ttl=5)
    existing_users = existing_users.dropna(how='all')
    existing_users["username"] = existing_users["username"].astype(str)

    # Search for the matching username
    matching_user = existing_users[existing_users["username"] == username]

    if not matching_user.empty:
        stored_hash = matching_user.iloc[0]["password"]
        if bcrypt.checkpw(password.encode(), stored_hash.encode()):
            return {
                "username": matching_user.iloc[0]["username"],
                "email": matching_user.iloc[0]["email"],
                "photo_path": matching_user.iloc[0]["photo_path"]
            }
    return None

# Face login
if use_face_login:
    st.write('⚠️由於 Streamlit 平台會不定時重製，因此已註冊帳號的 Face Login 功能會在重製後失效，請使用傳統文字 Login。')
    st.write("### 📷 Face Login")
    camera_photo = st.camera_input("Take a Snapshot")

    if camera_photo and st.button("Login with Face"):
        try:
            img = Image.open(camera_photo).convert('RGB')  # Ensure RGB format
            img_np = np.array(img)

            # Now detect face
            unknown_face_encodings = face_recognition.face_encodings(img_np)
            if not unknown_face_encodings:
                st.error('No face detected in captured image.')
                unknown_encoding = np.array([])
            else:
                unknown_encoding = unknown_face_encodings[0]

        except UnidentifiedImageError:
            st.error('Uploaded image format not supported.')
        except Exception as e:
            st.error(f'Image processing failed: {str(e)}')

        # Check known images
        if unknown_encoding.any():
            existing_users = conn.read(worksheet="Users", usecols=["username", "email", "photo_path"], ttl=5)
            existing_users = existing_users.dropna(subset=["photo_path"])  # Make sure we have valid photo paths

            user_result = {"status": "fail"}

            for _, user in existing_users.iterrows():
                username = str(user["username"])
                email = str(user["email"])
                photo_path = str(user["photo_path"])

                known_image_path = os.path.join("profile_photos", os.path.basename(photo_path))
                if os.path.exists(known_image_path):
                    known_image = face_recognition.load_image_file(known_image_path)
                    known_encodings = face_recognition.face_encodings(known_image)
                    if not known_encodings:
                        continue

                    match = face_recognition.compare_faces([known_encodings[0]], unknown_encoding, tolerance=0.4)
                    if match[0]:
                        user_result = {
                            "status": "success",
                            "data": {
                                "photo": known_image,
                                "username": username,
                                "email": email,
                            }
                        }
                        break
                else:
                    continue
        else:
            user_result = {
                        "status": "none",
                    }
            
        if user_result["status"] == "success":
            st.success("🎉 Face Login Successful")
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.email = email
            st.image(known_image, caption="User Photo", width=200)
            for k, v in user_result["data"].items():
                if k != "photo":
                    st.markdown(f"**{k.replace('_',' ').title()}:** {v}")
            st.rerun()
            
        elif user_result["status"]=="fail":
            st.error('Face not recognized. (如果你已經註冊過，那有可能 Streamlit 重製了)')
        else:
            pass

# Traditional Login       
else:
    st.write("### 🔐 Traditional Login")
    username = st.text_input(r"$\textsf{\Large Username}$")
    password = st.text_input(r"$\textsf{\Large Password}$", type="password")

    if st.button(r"$\textsf{\Large Login}$"):
        user = verify_credentials(username, password)

        if user:
            st.success("🎉 Login Successful")
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.email = user['email']
            user_data = {
                "username": user["username"],
                "email": user["email"],
            }
            for k, v in user_data.items():
                st.markdown(f"**{k.replace('_',' ').title()}:** {v}")
            st.rerun()
        else:
            st.error("Invalid username or password")

# Registration prompt
st.markdown("---")
if st.button("New User? Create Profile"):
    st.switch_page("pages/register.py")