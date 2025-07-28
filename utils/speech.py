from google import genai
from google.genai import types
import streamlit as st 

def speech_to_text(key: int):
    client = genai.Client(
        api_key=st.secrets['Gemini']['API_KEY']
    )

    config = types.GenerateContentConfig(
        system_instruction="Based on the **audio's** language, please respond with the same language as the **audio**."
    )

    audio = st.audio_input("語音輸入", key=key)

    def generate_language():
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=[
                """Please return what language this audio speech is in.
                    Example: AUDIO- I am 10 years old. RETURN- English
                    Example: AUDIO- 我現在十歲。 RETURN- Chinese (Default: Traditional)
                    Example: AUDIO- Ich bin sechzehn Jahre alt. RETURN- German""",
                types.Part.from_bytes(
                    data=audio,
                    mime_type='audio/mp3'
                )
            ],
        )
        return response.text

    def generate(language):
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=[
#               """Please create a transcript of the speech. Do not add any timestamps, just plain words.
#                   請建立語音的文字記錄。請勿添加任何時間戳，只需要說出的文字即可。
#                   Bitte erstellen Sie ein Transkript der Rede. Fügen Sie keine Zeitstempel hinzu, nur die einfachen Wörter.""", 
                f"""Please create a transcript of the speech. The speech is in {language}. 
                    Do not add any timestamps, just plain words.""",
                types.Part.from_bytes(
                    data=audio,
                    mime_type='audio/mp3'
                )
            ],
            config=config
        )
        return response.text

    if audio:
        audio = audio.read()
        text = generate(generate_language())
        st.write(text)
        return text
    
if __name__ == "__main__":
    st.title('語音辨識')
    st.write(speech_to_text())