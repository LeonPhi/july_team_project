import streamlit as st

#from forms.contact import contact_form


#@st.experimental_dialog("Contact Me")
#def show_contact_form():
#    contact_form()


# --- HERO SECTION ---
col1, col2 = st.columns(2, gap="small", vertical_alignment="center")
with col1:
    st.image("./assets/robot_logo.webp", width=230)

with col2:
    st.title("TEAM", anchor=False)
    st.write(
        "1234567890"
    )
#    if st.button("✉️ Contact Me"):
#        show_contact_form()


# --- EXPERIENCE & QUALIFICATIONS ---
st.write("\n")
st.subheader("Team Members", anchor=False)
st.write(
    """
    - 12345678
    - 12345678
    - 12345678
    """
)

# --- SKILLS ---
st.write("\n")
st.subheader("Skills", anchor=False)
st.write(
    """
    - 12345678
    - 12345678
    - 12345678
    """
)
