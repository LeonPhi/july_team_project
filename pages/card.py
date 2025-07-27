import streamlit as st
from PIL import Image
from io import BytesIO
from google import genai
from google.genai import types

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from email_validator import validate_email, EmailNotValidError
from email.message import EmailMessage
from email.mime.text import MIMEText
import base64

from utils.sidebar import render_sidebar
from utils.speech import speech_to_text

st.title("Greeting Card 賀卡")

key = st.secrets['Gemini']['API_KEY']
client = genai.Client(api_key=key)

if 'email' not in st.session_state:
     st.session_state.email = None

def text_language(text):
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=[
                f"""Please return what language this text is in: {text}
                    Example: TEXT- I am 10 years old. RETURN- English
                    Example: TEXT- 我現在十歲。 RETURN- Chinese
                    Example: TEXT- Ich bin sechzehn Jahre alt. RETURN- German""",
            ],
        )
        return response.text

def create_image():
    response = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=f"""
                    Generate a short e-mail, including the subject, text and a {occasion} greeting card. 
                    The style of the card should be clean, with vibrant pastel colors, 
                    soft lighting, and a heartwarming feel. Keep the background simple and elegant.

                    Details:{details}

                    **Don't ask for extra detail if empty, just generate a generic e-mail.**
                    **Don't add any extra explanations of the prompt, only subject, email and greeting card.**

                    Please reply in {lang}.
                """,
        config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE']
        )
    )

    # 顯示文字、圖片
    st.write(response.text)
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            image = Image.open(BytesIO((part.inline_data.data)))
            st.image(image, caption="賀卡", use_container_width=True)
            return response.text, image

client_id = st.secrets['gmail_client']['CLIENT_ID']
client_secret = st.secrets['gmail_client']['CLIENT_SECRET']
client_config = {
    "installed": {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uris": ['https://dailygenie.streamlit.app'],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token"
    }
}

def authorize_user():
    flow = Flow.from_client_config(
        client_config,
        scopes=['https://www.googleapis.com/auth/gmail.send'],
        redirect_uri='http://localhost:8501'  # Change to actual streamlit app link when deploying
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    st.link_button("Authorize Gmail Access", auth_url, disabled=True) # Turn off 'disabled' after Auth verified

    if 'code' in st.query_params:
        flow.fetch_token(code=st.query_params['code'])
        creds = flow.credentials
        st.session_state.credentials = creds
        st.success("Gmail Authorized!")

def send_email(sender, reciever, subject, body):
    service = build('gmail', 'v1', credentials=st.session_state.credentials)
    message = MIMEText(body)
    message['to'] = reciever
    message['from'] = sender
    message['subject'] = subject
    raw_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
    service.users().messages().send(userId='me', body=raw_message).execute()

# main code
use_speech = st.toggle(r"$\textsf{\Large 使用語音輸入}$", value=True)

if use_speech:
    st.text('請輸入節日、場合類型、慶祝事情等等')
    occasion = speech_to_text(1)
    st.text('可以加詳細說明 (如寄件者、收件者姓名，或其他要加在郵件或卡片裡的事物):')
    details = speech_to_text(2)
else:
    occasion = st.text_input(r'$\textsf{請輸入節日、場合類型、慶祝事情等等}$')
    details = st.text_input(r'$\textsf{可以加詳細說明 (如寄件者、收件者姓名和關係，或其他要加在郵件或卡片裡的事物):}$')

sender = st.session_state.email
st.write('\n')
st.text(f'你(寄件者)的 E-mail: {sender}')

# Remove after Auth verified
st.write(r'$\textsf{*很抱歉，尚未通過 OAuth 2.0 用戶端認證流程，寄送郵件功能這幾天無法使用。}$')
st.write('Sorry, Gmail delivery feature is not available for the next few days as the OAuth 2.0 client authentication process has not been completed.')

authorize_user()

reciever = st.text_input(r'$\textsf{請輸入收件者 E-mail (Gmail only):}$', disabled=True) # Turn off 'disabled' after Auth verified

if occasion:
#    if not st.session_state['credentials']:
#        st.info('Please authorize your Gmail.')
#    if reciever:
#        try:
#            v = validate_email(reciever)
#            reciever = v.normalized
            if st.button('生成電子郵件、賀卡'):
                with st.spinner('請稍等...'):
                    lang = text_language(occasion)
                    text, image = create_image()
                    split_text = text.split(':', maxsplit=1)[1].split('\n', maxsplit=1)
                    subject, body = split_text[0].strip(), split_text[1].strip()
#                    if st.button("Send Email"):
#                        send_email(sender, reciever, subject, body)
#        except EmailNotValidError as e:
#            st.error('Invalid E-mail 無效的電子郵件: ' + str(e))
#    else:
#        st.info('請先輸入收件者的 E-mail.')

# Uncomment above after Auth verified

render_sidebar()
