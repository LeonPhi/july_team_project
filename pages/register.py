import streamlit as st
import base64
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from email_validator import validate_email, EmailNotValidError
from zxcvbn import zxcvbn   # Password strength checker
import bcrypt
import os


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


if 'submitted' not in st.session_state:
    st.session_state.submitted = False

conn = st.connection('sqlite', type='sql')

# Function to create the table if it doesn't exist
def create_table():
    with conn.session as s:
        s.execute(text('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT UNIQUE,
                password TEXT,
                email TEXT,
                photo_path TEXT
            )
        '''))
        s.commit()

# Save uploaded photo to a directory
def save_photo(photo, username):
    directory = "profile_photos"
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, f"{username}.jpg")
    with open(filepath, "wb") as f:
        f.write(photo.getbuffer())
    return filepath

# Function to add new user
def register_user(username, password, email, photo_path):
    v = validate_email(email)
    email = v.normalized
    
    with conn.session as s:
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        try:
            s.execute(
                text("""
                    INSERT INTO users (username, password, email, photo_path)
                    VALUES (:username, :password, :email, :photo_path)
                """),
                {
                    "username": username,
                    "password": hashed_pw,
                    "email": email,
                    "photo_path": photo_path
                }
            )
            s.commit()
            return True
        except IntegrityError:
            return False
        finally:
            s.commit()

st.title("📝 Register 註冊")

username = st.text_input(r"$\textsf{\Large Username}$")
password = st.text_input(r"$\textsf{\Large Password}$", type='password')

if password:
    result = zxcvbn(password, user_inputs=[username])
    score = result['score']  # 0 to 4
    suggestions = result['feedback']['suggestions']

    col1, col2 = st.columns([4,6]) 
    with col1:
        if score < 2:
            st.write(r"$\textsf{Password Strength: 弱 Weak}$")
        elif score == 2:
            st.write(r"$\textsf{Password Strength: 好 Ok}$")
        else:
            st.write(r"$\textsf{Password Strength: 強 Strong}$")
    with col2:
        st.progress((score + 1) * 20)  # Converts 0–4 to 20–100%
        
    if suggestions:
        st.markdown("**Suggestions:**")
        for tip in suggestions:
            st.write(f"• {tip}")
    else:
        st.success("Your password looks strong!")

with st.form("register_form"):

    email = st.text_input(r"$\textsf{\Large Email (請使用 Gmail)}$")

    uploaded_photo = st.file_uploader(r"$\textsf{\Large Option 1: Upload Profile Photo (JPG, PNG)}$", type=["jpg", "jpeg", "png"])
    st.subheader("Option 2: 📷 Capture Your Face Photo")
    camera_photo = st.camera_input("Take a Snapshot")

    submitted = st.form_submit_button("Register")

if submitted:
    st.session_state["submitted"] = True

    with st.spinner("請稍等..."):
        create_table()

        if not uploaded_photo and not camera_photo:
            st.warning("📸 Please upload a profile photo for face recognition.")
        elif not all([username, password, email]):
            st.warning("⚠️ Please fill out all fields before submitting.")
        else:
            if score < 2:
                st.warning('Password not strong enough.')
            else:
                if camera_photo:
                    photo_path = save_photo(camera_photo, username)
                else:
                    photo_path = save_photo(uploaded_photo, username)
                try:
                    success = register_user(username, password, email, photo_path)
                    if success:
                        st.success(f"🎉 Welcome, {username}! You’ve been registered.")
                        st.switch_page("pages/login.py")
                        st.image(uploaded_photo, caption="Saved Profile Photo", width=180)
                    else:
                        st.error("😢 Username already taken. Try another one.")
                except AttributeError as e:
                    if "'NoneType' object has no attribute 'format'" in str(e):
                        pass  # Silently ignore this harmless error
                    else:
                        st.error(f"🚨 Registration failed: {e}")
                except Exception as e:
                    st.error(f"🚨 Registration failed: {e}")
