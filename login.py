import streamlit as st
from PIL import Image
import requests
from io import BytesIO


LOGO_URL = "https://raw.githubusercontent.com/ZODOPT-Tech/Wheelbrand/main/images/zodopt.png"


def apply_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #F6F8FB;
        color: #1A1F36;
    }

    [data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }

    .left-panel {
        text-align: center;
        padding-top: 80px;
    }

    .details {
        margin-top: 35px;
        font-size: 16px;
        font-weight: 500;
        line-height: 2.2;
    }

    .title {
        font-size: 32px;
        font-weight: 800;
        margin-bottom: 28px;
        margin-top: 60px;
        color: #0B2A63;
    }

    /* Labels */
    label {
        font-size: 15px !important;
        font-weight: 600 !important;
        margin-bottom: 6px !important;
        color: #1A1F36 !important;
    }

    .stTextInput > div > div > input {
        border-radius: 8px;
        height: 46px;
        background: white;
        font-size: 15px;
        border: 1px solid #CBD5E0;
    }

    /* Primary Button */
    .primary-btn > button {
        width: 100%;
        height: 48px;
        border: none;
        border-radius: 8px;
        font-size: 17px;
        font-weight: 700;
        background: #0B2A63;
        color: white;
    }

    .secondary-btn > button {
        background: #0B2A63;
        color: white;
        width: 180px;
        height: 42px;
        border-radius: 8px;
        font-size: 15px;
        font-weight: 600;
        border: none;
    }

    .secondary-container {
        display: flex;
        gap: 20px;
        justify-content: center;
        margin-top: 14px;
    }
    </style>
    """, unsafe_allow_html=True)


def render(navigate):
    st.set_page_config(layout="wide")
    apply_styles()

    left, right = st.columns([1, 1])

    # Left Side
    with left:
        st.markdown("<div class='left-panel'>", unsafe_allow_html=True)
        try:
            logo = Image.open(BytesIO(requests.get(LOGO_URL).content))
            st.image(logo, width=330)
        except:
            st.write("Logo Load Error")

        st.markdown("""
        <div class="details">
        📞 Phone: +123-456-7890 <br>
        ✉️ Email: hello@vclarifi.com <br>
        🌐 Website: www.vclarifi.com <br>
        📍 India
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Right Side
    with right:
        st.markdown("<div class='title'>LOGIN TO YOUR ACCOUNT</div>", unsafe_allow_html=True)

        # Labels now visible
        email = st.text_input("Email Address", label_visibility="visible")
        password = st.text_input("Password", type="password", label_visibility="visible")

        # Primary login button - wider
        st.markdown("<div class='primary-btn'>", unsafe_allow_html=True)
        if st.button("Login"):
            navigate("Dashboard")
        st.markdown("</div>", unsafe_allow_html=True)

        # Secondary buttons side by side
        st.markdown("<div class='secondary-container'>", unsafe_allow_html=True)

        col_forgot, col_create = st.columns(2)

        with col_forgot:
            st.markdown("<div class='secondary-btn'>", unsafe_allow_html=True)
            if st.button("Forgot Password?"):
                navigate("Forgot")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_create:
            st.markdown("<div class='secondary-btn'>", unsafe_allow_html=True)
            if st.button("Create Account"):
                navigate("Signup")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
