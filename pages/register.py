import streamlit as st
import sqlite3
import bcrypt
import os

# Function to create the table if it doesn't exist
def create_table():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT UNIQUE,
            password TEXT,
            email TEXT,
            photo_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

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
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)",
                       (username, hashed_pw, email, photo_path))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.commit()
        conn.close()


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
#               st.error(f"🚨 Registration failed: {repr(e)}")
                pass
