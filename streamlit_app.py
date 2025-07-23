import streamlit as st

st.markdown(
            """
            <style>
            [data-testid="stSidebarNavItems"] {
                max-height: none;
            }
           </style>
           """,
            unsafe_allow_html=True
        )

# --- PAGE SETUP ---
about_page = st.Page(
    "pages/about_team.py",
    title="About Team",
    icon=":material/account_circle:",
)
recipe_page = st.Page(
    "pages/recipe.py",
    title="Recipe",
    icon=":material/account_circle:",
)
music_page = st.Page(
    "pages/music.py",
    title="Music",
    icon=":material/account_circle:",
)
accounting_page = st.Page(
    "pages/accounting.py",
    title="Accounting",
    icon=":material/account_circle:",
)
calendar_page = st.Page(
    "pages/calendar.py",
    title="Calendar",
    icon=":material/account_circle:",
)
login_page = st.Page(
    "pages/login.py",
    title="Log In",
    icon=":material/login:",
    default=True,
)
register_page = st.Page(
    "pages/register.py",
    title="Register",
    icon=":material/person_add:",
)



# --- NAVIGATION SETUP [WITHOUT SECTIONS] ---
# pg = st.navigation(pages=[about_page, project_1_page, project_2_page])

# --- NAVIGATION SETUP [WITH SECTIONS]---
pg = st.navigation(
    {
        "Info": [about_page],
        "Programs": [recipe_page, music_page, accounting_page, calendar_page],
        "Account": [login_page, register_page]
    }
)


# --- SHARED ON ALL PAGES ---
st.logo("assets/codingisfun_logo.png")
st.sidebar.markdown("Made with ❤️ by Team")


# --- RUN NAVIGATION ---
pg.run()
