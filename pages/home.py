import streamlit as st
import base64
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection
from utils.sidebar import render_sidebar


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

st.title("Voting 投票")

#st.toast(f"👋 嗨, {st.session_state.username}!")

conn = st.connection("gsheets", type=GSheetsConnection)
existing_data = conn.read(worksheet="Votes", usecols=list(range(2)), ttl=0)
user = st.session_state.username
already_voted = existing_data["username"].dropna(how='all').astype(str).str.contains(user).any()

# Already voted
if already_voted:
    st.info("已投票")
    vote_counts = existing_data['vote'].value_counts().reset_index()
    vote_counts.columns = ['Category 類別', 'Votes 票數']
    all_categories = [
        "Recipe 食譜推薦",
        "Bookkeeping 記帳",
        "Identify Item 物品辨識",
        "Music 音樂",
        "Greeting Card 賀卡",
    ]
    color_map = {
        'Recipe 食譜推薦': "#FF3232",
        'Bookkeeping 記帳': "#FFA333",
        'Identify Item 物品辨識': "#F8FF24",
        'Music 音樂': "#51FF2E",
        'Greeting Card 賀卡': "#2365FF"
    }

    # Include all categories, even ones with no votes
    full_vote_df = pd.DataFrame({'Category 類別': all_categories})
    full_vote_df = full_vote_df.merge(vote_counts, on='Category 類別', how='left')
    full_vote_df['Votes 票數'] = full_vote_df['Votes 票數'].fillna(0).astype(int)
    bar_colors = full_vote_df['Category 類別'].map(color_map)

    # Bar chart
    fig = px.bar(
        full_vote_df,
        x='Votes 票數',
        y='Category 類別',
        orientation='h',
        text='Votes 票數',
        title='\t\t\t\t\t\t\t📊 Current Vote Totals 現在投票結果'
    )

    fig.update_traces(marker_color=bar_colors,
                      textposition='outside',
                      textfont=dict(size=22))
    fig.update_layout(xaxis=dict(showticklabels=False), 
                      yaxis=dict(categoryorder='total ascending', 
                      tickfont=dict(size=18)))

    # Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)

# Hasn't voted yet
else:
    st.write(r'$\textsf{\Large 請選擇你最喜歡的功能:}$')
    st.write("(每個功能先用用看再投票)")
    st.write('\n')
    st.write('\n')
    st.write(r'$\textsf{\Large Please choose your favorite program/function:}$')
    st.write("(Try out all the programs/functions before voting)")

    vote = st.selectbox("功能 Programs", [
                                            "Recipe 食譜推薦",
                                            "Bookkeeping 記帳",
                                            "Identify Item 物品辨識",
                                            "Music 音樂",
                                            "Greeting Card 賀卡",
                                        ], index=None)

    if vote:
        if st.button('投票'):

            entry = pd.DataFrame([{
                "username": st.session_state.username,
                "vote": vote
            }])

            updated_data = pd.concat([existing_data, entry], ignore_index=True)
            conn.update(worksheet="Votes", data=updated_data)
            st.rerun()


render_sidebar()
