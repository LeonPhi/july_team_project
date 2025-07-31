### OSError: [Errno 24] inotify instance limit reached (on cloud after deploy)
### Solution: Add "inotify" to requirements.txt, 
### Then add this to secrets.toml:
### [server]
### fileWatcherType = "none"

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

st.markdown(
    """
    <style>
    /* Target the span inside the navigation link */
    div[data-testid="stSidebarNav"] ul li a span {
        font-size: 16px !important;
    }

    /* Optional: tweak section headers if used */
    div[data-testid="stSidebarNav"] header {
        font-size: 24px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

if "email" not in st.session_state:
    st.session_state.email = None

if "credentials" not in st.session_state:
    st.session_state.credentials = False

# --- PAGE SETUP ---
vote_page = st.Page(
    "pages/home.py",
    title="Vote!",
    icon=":material/how_to_vote:",
)
recipe_page = st.Page(
    "pages/recipe.py",
    title="Recipe",
    icon=":material/chef_hat:"
)
expense_page = st.Page(
    "pages/expense.py",
    title="Bookkeeping",
    icon=":material/checkbook:",
)
expense_data_page = st.Page(
    "pages/expense_data.py",
    title="Expense Data",
    icon=":material/paid:",
)
identify_page = st.Page(
    "pages/item_identify.py",
    title="Identify Item",
    icon=":material/feature_search:",
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
        "Voting": [vote_page],
        "Programs": [recipe_page, expense_page, expense_data_page, identify_page, music_page, card_page],
        "Info": [about_page],
    })
else:
    pg = st.navigation({
        "Account": [login_page, register_page],  # Only login/register
        "Info": [about_page],
    })

# --- SHARED ON ALL PAGES ---
st.logo("assets/codingisfun_logo.png")
st.sidebar.subheader("Made with ❤️ by Team")


# --- RUN NAVIGATION ---
pg.run()
