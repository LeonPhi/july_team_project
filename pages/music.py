import streamlit as st
import cv2 
from deepface import DeepFace
from PIL import Image
import numpy as np 
import webbrowser
from utils.sidebar import render_sidebar

st.title("Music 音樂 (Just for fun)")

lang = st.text_input(r"$\textsf{\Large Language 語言}$")
singer = st.text_input(r"$\textsf{\Large Singer 歌手}$")
age_range = st.radio("", [
							"Kids", 
	   						"Teens", 
							"Mature"
						 ],
					index=None, horizontal=True)

camera_photo = st.camera_input(r"$\textsf{\Large 你現在的情緒: }$")

if camera_photo:
	if st.button('偵測情緒'):
		img = Image.open(camera_photo)
		img_array = np.array(img)
		img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
		result = DeepFace.analyze(
  			img_path = img_bgr, actions = ['emotion'],
			enforce_detection = False
		)
		st.session_state.emotion = result[0]["dominant_emotion"]
		st.write(r"$\textsf{\Large " + st.session_state.emotion + "}$")

emotion = st.session_state.get("emotion", None)
st.write(r"$\textsf{\Large " + emotion + "}$")

if st.button(r"$\textsf{推薦音樂 Recommed Songs}$"):
	if not(emotion):
		st.warning("請先偵測情緒")
	elif not(age_range):
		st.warning("請先選類別")
	else:
		webbrowser.open(f"https://www.youtube.com/results?search_query={lang}+{emotion}+song+{singer}+{age_range}")

render_sidebar()
