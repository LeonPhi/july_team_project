import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
import bcrypt
import os

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

with st.form("register_form"):
    username = st.text_input(r"$\textsf{\Large Username}$")
    password = st.text_input(r"$\textsf{\Large Password}$", type='password')
    email = st.text_input(r"$\textsf{\Large Email}$")

    uploaded_photo = st.file_uploader(r"$\textsf{\Large Option 1: Upload Profile Photo (JPG, PNG)}$", type=["jpg", "jpeg", "png"])
    st.subheader("Option 2: 📷 Capture Your Face Photo")
    camera_photo = st.camera_input("Take a Snapshot")

    submitted = st.form_submit_button("Register")

if submitted:
    with st.spinner("請稍等..."):
        create_table()

        if not uploaded_photo and not camera_photo:
            st.warning("📸 Please upload a profile photo for face recognition.")
        elif not all([username, password, email]):
            st.warning("⚠️ Please fill out all fields before submitting.")
        else:
            if camera_photo:
                photo_path = save_photo(camera_photo, username)
            else:
                photo_path = save_photo(uploaded_photo, username)
            try:
                success = register_user(username, password, email, photo_path)
                if success:
                    st.success(f"🎉 Welcome, {username}! You’ve been registered.")
                    st.image(uploaded_photo, caption="Saved Profile Photo", width=180)
                else:
                    st.error("😢 Username already taken. Try another one.")
            except Exception as e:
               st.error(f"🚨 Registration failed: {repr(e)}")
            pass
