import streamlit as st
from PIL import Image
import requests
from io import BytesIO


LOGO_URL = "https://raw.githubusercontent.com/ZODOPT-Tech/Wheelbrand/main/images/zodopt.png"


def apply_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #F4F6FA;
        color: #1A1F36;
    }

    [data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }

    /* Left panel */
    .left-panel {
        text-align: center;
        padding-top: 80px;
    }

    .details {
        margin-top: 35px;
        font-size: 16px;
        font-weight: 500;
        color: #1A1F36;
        line-height: 2.1;
    }

    /* Form title */
    .title {
        font-size: 30px;
        font-weight: 800;
        text-align: left;
        margin-bottom: 28px;
        margin-top: 50px;
        color: #0B2A63;
    }

    /* Inputs */
    .stTextInput > div > div > input {
        border-radius: 8px;
        height: 45px;
        font-size: 15px;
        background: white;
        border: 1px solid #D2D8E4;
    }

    /* Login Button */
    .login-btn > button {
        width: 100%;
        height: 46px;
        border: none;
        color: white;
        border-radius: 8px;
        font-size: 17px;
        font-weight: 700;
        background: #0B2A63;
    }

    /* Bottom inline links */
    .bottom-links {
        display: flex;
        justify-content: center;
        gap: 18px;
        margin-top: 18px;
        font-size: 15px;
        font-weight: 600;
        color: #0B2A63;
    }

    .link {
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)


def render(navigate):
    st.set_page_config(layout="wide")
    apply_styles()

    left, right = st.columns([1, 1])

    # Left side
    with left:
        st.markdown("<div class='left-panel'>", unsafe_allow_html=True)
        try:
            logo = Image.open(BytesIO(requests.get(LOGO_URL).content))
            st.image(logo, width=300)
        except:
            st.write("Logo load error")

        st.markdown("""
        <div class="details">
        📞 Phone: +123-456-7890 <br>
        ✉️ Email: hello@vclarifi.com <br>
        🌐 Website: www.vclarifi.com <br>
        📍 India
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Right side (Login Form)
    with right:
        st.markdown("<div class='title'>LOGIN TO YOUR ACCOUNT</div>", unsafe_allow_html=True)

        email = st.text_input("Email Address")
        pwd = st.text_input("Password", type="password")

        st.markdown("<div class='login-btn'>", unsafe_allow_html=True)
        if st.button("Login"):
            navigate("Dashboard")
        st.markdown("</div>", unsafe_allow_html=True)

        # Inline links (no buttons)
        st.markdown("<div class='bottom-links'>", unsafe_allow_html=True)

        if st.button("Forgot Password?", key="forgot"):
            navigate("Forgot")

        if st.button("Create Account", key="signup"):
            navigate("Signup")

        st.markdown("</div>", unsafe_allow_html=True)
