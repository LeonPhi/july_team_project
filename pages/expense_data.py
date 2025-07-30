import streamlit as st
from streamlit_gsheets import GSheetsConnection
import base64
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.sidebar import render_sidebar


image_path = "assets/08.jpg"
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


st.title("Expense Data 消費資料")

conn = st.connection("gsheets", type=GSheetsConnection)

def get_week_of_month(date):
    first_day = date.replace(day=1)
    dom = date.day
    adjusted_dom = dom + first_day.weekday()
    return (adjusted_dom - 1) // 7 + 1

df = conn.read(worksheet="Expenses", usecols=["username", "date", "type", "total"], ttl=5)
user_data = df[df["username"] == st.session_state.username].copy()
user_data["date"] = pd.to_datetime(user_data["date"])

type_color_map = {
    "交通": "#FF4040",
    "餐飲": "#FFE137",
    "娛樂": "#1CCAFF",
    "醫療保健": "#27FF52",
    "住房": "#242424",
    "購物": "#6827FF",
    "禮品": "#FF7F17",
    "其他": "#A8A8A8"  # fallback or miscellaneous category
}

### Daily Expenses-------------------------------------------------
# Filter by chosen date

spent_days = user_data[user_data["total"] > 0]["date"].dt.date.drop_duplicates()
spent_days = sorted(spent_days, reverse=True)
spent_days_str = [day.strftime("%Y-%m-%d") for day in spent_days]
selected_day_str = st.selectbox(r"$\textsf{\Large 選擇消費日期}$", spent_days_str)
selected_day = pd.to_datetime(selected_day_str).date()
#selected_day = st.date_input(r'$\textsf{選擇日期}$', value=pd.Timestamp.today())
daily_data = user_data[user_data["date"].dt.date == selected_day]

# Group by 'type'
daily_summary = daily_data.groupby("type")["total"].sum().reset_index()

st.subheader(f"{selected_day} 的消費")
fig = px.bar(daily_summary, x="type", y="total", color="type",
             title=f"每日消費分類 ({selected_day})",
             labels={"type": "類別", "total": "金額 (NTD)"},
            color_discrete_map=type_color_map,)
st.plotly_chart(fig, use_container_width=True)



st.write('\n')
st.write('\n')

### Weekly Expenses -----------------------------------------------
user_data["year"] = user_data["date"].dt.year
user_data["month_num"] = user_data["date"].dt.month
user_data["month_name"] = user_data["date"].dt.strftime("%b")  # e.g., 'Jul'
user_data["week_of_month"] = user_data["date"].apply(get_week_of_month)
user_data["month_year"] = user_data["year"].astype(str) + " " + user_data["month_name"].astype(str)
user_data["month_week"] = user_data["month_year"] + " 第" + user_data["week_of_month"].astype(str) + "週"

st.subheader("Weekly Expenses Overview")

selected_year = st.selectbox(r"$\textsf{\Large 選擇年份}$", sorted(user_data["year"].unique(), reverse=True))
months_in_year = user_data[user_data["year"] == selected_year]["month_num"].unique()
month_options = {num: user_data[user_data["month_num"] == num]["month_name"].iloc[0] for num in months_in_year}
selected_month = st.selectbox(r"$\textsf{\Large 選擇月份}$", [month_options[num] for num in sorted(month_options)])

filtered_data = user_data[
    (user_data["year"] == selected_year) &
    (user_data["month_name"] == selected_month)
].copy()

active_weeks = sorted(week for week in filtered_data["week_of_month"].unique()
                      if filtered_data[filtered_data["week_of_month"] == week]["total"].sum() > 0)
selected_week = st.selectbox(
    r"$\textsf{\Large 選擇週次 (圓餅圖)}$", 
    active_weeks, 
    format_func=lambda x: f"{selected_year} {selected_month} 第{x}週"
)

week_data = filtered_data[filtered_data["week_of_month"] == selected_week]
week_by_type = week_data.groupby("type")["total"].sum().reset_index()

weekly_summary = user_data.groupby(["month_year", "month_week"])["total"].sum().reset_index()
 


fig_week = px.bar(weekly_summary, x="month_week", y="total",
                title="每週消費表", labels={"month_week": "週次", "total": "總支出 Total (NTD)"})
st.plotly_chart(fig_week, use_container_width=True)


fig_pie = go.Figure(
    data=[go.Pie(
        labels=week_by_type["type"],
        values=week_by_type["total"],
        marker=dict(colors=[type_color_map.get(t, "#A8A8A8") for t in week_by_type["type"]]),
        textinfo="label+percent",
        hoverinfo="label+value",
        hole=0.3  # Optional: makes it a donut chart!
    )]
)

fig_pie.update_layout(title=f"{selected_year} {selected_month} 第{selected_week}週 消費分布")

st.plotly_chart(fig_pie, use_container_width=True)

render_sidebar()