import streamlit as st
from PIL import Image
import requests
from io import BytesIO

# ---------------- CONSTANTS ----------------
LOGO_URL = "https://raw.githubusercontent.com/ZODOPT-Tech/Wheelbrand/main/images/zodopt.png"
PRIMARY_COLOR = "#0B2A63"


# ---------------- STYLES ----------------
def apply_styles():
    st.markdown(f"""
    <style>

    /* GLOBAL FONT */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {{
        font-family: "Inter", sans-serif;
        background-color: #F6F8FB;
    }}

    [data-testid="stHeader"] {{
        background: transparent;
    }}

    /* LEFT PANEL */
    .left-panel {{
        text-align: center;
        padding-top: 90px;
    }}

    .contact {{
        margin-top: 40px;
        font-size: 16px;
        font-weight: 500;
        line-height: 2.2;
        color: #1A1F36;
        text-align: left;
        width: 330px;
        margin-left: auto;
        margin-right: auto;
    }}

    /* RIGHT PANEL TITLE */
    .title {{
        font-size: 34px;
        font-weight: 800;
        margin-bottom: 35px;
        margin-top: 90px;
        color: {PRIMARY_COLOR};
        text-align: left;
    }}

    /* LABELS */
    .stTextInput label {{
        display: block !important;
        margin-bottom: 6px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        color: #1A1F36 !important;
    }}

    /* INPUT */
    .stTextInput > div > div > input {{
        border-radius: 8px !important;
        height: 46px !important;
        background: white !important;
        font-size: 15px !important;
        border: 1px solid #CBD5E0 !important;
    }}

    /* BUTTONS GLOBAL STYLE */
    .stButton > button {{
        background-color: {PRIMARY_COLOR} !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        cursor: pointer;
    }}

    /* PRIMARY LOGIN BUTTON FULL WIDTH */
    .login-btn > button {{
        width: 100% !important;
        height: 48px !important;
        font-size: 17px !important;
        font-weight: 700 !important;
        margin-top: 12px;
    }}

    /* SECONDARY BUTTONS INLINE */
    .button-row {{
        display: flex;
        justify-content: center;
        gap: 32px;
        margin-top: 20px;
    }}

    .button-row .stButton > button {{
        width: 210px !important;
        height: 44px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
    }}

    </style>
    """, unsafe_allow_html=True)


# ---------------- PAGE UI ----------------
def render(navigate):
    st.set_page_config(layout="wide")
    apply_styles()

    left, right = st.columns([1.1, 1])

    # -------- LEFT PANEL --------
    with left:
        st.markdown("<div class='left-panel'>", unsafe_allow_html=True)

        try:
            logo = Image.open(BytesIO(requests.get(LOGO_URL).content))
            st.image(logo, width=330)
        except:
            st.write("Logo failed")

        st.markdown("""
        <div class="contact">
        📞 Phone: +123-456-7890 <br>
        ✉️ Email: hello@vclarifi.com <br>
        🌐 Website: www.vclarifi.com <br>
        📍 India
        </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # -------- RIGHT PANEL --------
    with right:
        st.markdown("<div class='title'>LOGIN TO YOUR ACCOUNT</div>", unsafe_allow_html=True)

        # Inputs
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")

        # Login Button
        st.markdown("<div class='login-btn'>", unsafe_allow_html=True)
        if st.button("Login"):
            navigate("Dashboard")
        st.markdown("</div>", unsafe_allow_html=True)

        # Secondary Buttons
        st.markdown("<div class='button-row'>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Forgot Password?"):
                navigate("Forgot")

        with col2:
            if st.button("Create Account"):
                navigate("Signup")

        st.markdown("</div>", unsafe_allow_html=True)


# ---------------- SAMPLE NAVIGATION ----------------
if __name__ == "__main__":
    def dummy_navigate(page):
        st.success(f"Navigate → {page}")

    render(dummy_navigate)
