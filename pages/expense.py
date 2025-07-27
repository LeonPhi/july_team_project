import streamlit as st
from google import genai
from google.genai import types
from utils.sidebar import render_sidebar

st.title("Bookkeeping 記帳")

client = genai.Client(
        api_key=st.secrets['Gemini']['API_KEY']
    )

config = types.GenerateContentConfig(
        system_instruction=""
    )










render_sidebar()