from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from IPython.display import Image, display
from google import genai
from google.genai import types
from PIL import Image as Image1
from io import BytesIO
import os
import base64
import streamlit as st

key = st.secrets['Gemini']['API_KEY']

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=key,
)

client = genai.Client(
        api_key=key,
)

st.title('Recipe 食譜推薦')

# 假設使用者資訊
user_profile = {
    "age": 30,
    #"conditions": ["高血壓", "糖尿病"],
    "conditions": ["過胖"],
    "dietary_preferences": ["過敏原:花生"],
}

#user_input = "雞蛋、牛奶、麵包、香蕉、蘋果、奶油，請給中式早餐食譜。"
user_input = st.text_input('''請輸入食品材料、年紀、身體狀況、過敏原和飲食偏好。
                           (也可以描述你要的樣式 (中式西式、早餐晚餐等等) )''', key=1)
#image_urls = [
#   "https://nutritionsource.hsph.harvard.edu/wp-content/uploads/2024/11/AdobeStock_118383793.jpeg",
#   "https://orchardfruit.com/cdn/shop/files/Red-Onion-1-lb.-The-Orchard-Fruit-72141081.jpg?crop=center&height=1200&v=1722937869&width=1200",
#   "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRids7Po0FF0aWy4bj3sjHO3KfzUsaEjCjQ1w&s",
#   "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSzlXU9AXfNSFjZmBsOW-JyvP6WEhJL1eOSHA&s",
#   "https://images.albertsons-media.com/is/image/ABS/136200003-ECOM?$ng-ecom-pdp-desktop$&defaultImage=Not_Available",
#]
images = []
uploaded_file = st.file_uploader("也可以輸入材料圖片 (最多4張)", type=["png", "jpeg", "jpg", "webp", "avif"], accept_multiple_files=True)
if uploaded_file:
    for i in range(len(uploaded_file)):
        uploaded_file[i] = uploaded_file[i].read()
        images.append(uploaded_file[i])

# Gemini prompt
prompt = f"""
你是食譜推薦小幫手，會描述年紀、身體狀況、過敏原和飲食偏好。

使用者的食品材料和建議等等是：「{user_input}」。

請幫我：
1. 根據使用者的年齡、健康狀況和有的材料等，推薦一個適合的食譜
2. 回答請用繁體中文
3. 都不用太多字，簡潔明瞭
"""

user_messages = [{"type": "text", "text": prompt}]
if images:
    if len(images) > 1:
       for image in images:
           encoded_image = base64.b64encode(image).decode("utf-8")
           user_messages.append({
               "type": "image_url",
               "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}
           })
    else:
       # 如果只有一張圖片，直接使用
        img_messages = [{"type": "image_url", "image_url": {"url": images[0]}}]
        img_messages.append({"type": "text", "text": "請描述照片裡有什麼食物。"})
        img_result = llm.invoke([HumanMessage(content=img_messages)])
        user_messages.append({"type": "text", "text": img_result.content})
human_messages = HumanMessage(content=user_messages)

if st.button('生成食譜'):
    result = llm.invoke([human_messages])
    st.text_area('AI', result.content, height=400)

    # 生成圖片
    contents = (result.content + "\n請根據上述食譜生成一張完成的料理圖片，逼真、無文字。").strip()

    response = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=contents,
        config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE']
        )
    )
    # 顯示輸出
    #print("🧠 Gemini 建議：\n")
    #print(result.content)
    # 顯示圖片
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            image = Image1.open(BytesIO((part.inline_data.data)))
            #display(image)
            st.image(image, caption="生成的料理圖片", use_container_width=True)
