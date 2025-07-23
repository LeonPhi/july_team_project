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

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- PAGE SETUP ---
home_page = st.Page(
    "pages/home.py",
    title="Home",
    icon=":material/home:",
)
recipe_page = st.Page(
    "pages/recipe.py",
    title="Recipe",
    icon=":material/chef_hat:",
)
accounting_page = st.Page(
    "pages/accounting.py",
    title="Accounting",
    icon=":material/checkbook:",
)
music_page = st.Page(
    "pages/music.py",
    title="Music",
    icon=":material/music_note:",
)
card_page = st.Page(
    "pages/card.py",
    title="Greeting Card",
    icon=":material/style:",
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
about_page = st.Page(
    "pages/about_team.py",
    title="About Team",
    icon=":material/account_circle:",
)

# --- NAVIGATION SETUP [WITHOUT SECTIONS] ---
# pg = st.navigation(pages=[about_page, project_1_page, project_2_page])

# --- NAVIGATION SETUP [WITH SECTIONS]---
if st.session_state.logged_in:
    pg = st.navigation({
        "Homepage": [home_page],
        "Programs": [recipe_page, accounting_page, music_page, card_page],
        "Info": [about_page],
    })
else:
    pg = st.navigation({
        "Account": [login_page, register_page],  # Only login/register
        "Info": [about_page],
    })

# --- SHARED ON ALL PAGES ---
st.logo("assets/codingisfun_logo.png")
st.sidebar.markdown("Made with ❤️ by Team")


# --- RUN NAVIGATION ---
pg.run()
