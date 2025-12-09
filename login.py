import streamlit as st
from PIL import Image
import requests
from io import BytesIO


LOGO_URL = "https://raw.githubusercontent.com/ZODOPT-Tech/Wheelbrand/main/images/zodopt.png"

PRIMARY_COLOR = "#0B2A63"


def apply_styles():
    st.markdown(f"""
    <style>

    /* GLOBAL FONT */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Inter', sans-serif;
        background-color: #F6F8FB;
        color: #1A1F36;
    }}

    [data-testid="stHeader"] {{
        background: transparent;
    }}

    /* LEFT PANEL */
    .left-panel {{
        text-align: center;
        padding-top: 70px;
    }}

    .contact {{
        margin-top: 35px;
        font-size: 16px;
        font-weight: 500;
        line-height: 2.2;
        color: #1A1F36;
    }}

    /* TITLE */
    .title {{
        font-size: 33px;
        font-weight: 800;
        margin-bottom: 32px;
        margin-top: 60px;
        color: {PRIMARY_COLOR};
        text-align:left;
    }}

    /* LABEL FIX */
    .stTextInput label {{
        display: block !important;
        margin-bottom: 6px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        color: #1A1F36 !important;
    }}

    /* INPUT BOX */
    .stTextInput > div > div > input {{
        border-radius: 8px !important;
        height: 46px !important;
        background: white !important;
        font-size: 15px !important;
        border: 1px solid #CBD5E0 !important;
    }}

    /* MAIN BUTTON FIX */
    .stButton > button {{
        background: {PRIMARY_COLOR} !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        height: 48px !important;
        width: 100% !important;
        font-weight: 700 !important;
        font-size: 17px !important;
        cursor: pointer;
    }}

    /* SECONDARY BUTTONS */
    .sec-btn > button {{
        background: {PRIMARY_COLOR} !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        height: 44px !important;
        width: 200px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        cursor: pointer;
        text-align:center;
    }}

    .sec-container {{
        display: flex;
        justify-content: center;
        gap: 30px;
        margin-top: 18px;
    }}

    </style>
    """, unsafe_allow_html=True)


def render(navigate):
    st.set_page_config(layout="wide")
    apply_styles()

    left, right = st.columns([1.1, 1])

    # LEFT
    with left:
        st.markdown("<div class='left-panel'>", unsafe_allow_html=True)
        try:
            logo = Image.open(BytesIO(requests.get(LOGO_URL).content))
            st.image(logo, width=330)
        except:
            st.write("Logo Load Error")

        st.markdown("""
        <div class="contact">
        📞 Phone: +123-456-7890 <br>
        ✉️ Email: hello@vclarifi.com <br>
        🌐 Website: www.vclarifi.com <br>
        📍 India
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # RIGHT
    with right:
        st.markdown("<div class='title'>LOGIN TO YOUR ACCOUNT</div>", unsafe_allow_html=True)

        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")

        # FULL WIDTH LOGIN
        if st.button("Login"):
            navigate("Dashboard")

        # SECONDARY BUTTONS INLINE
        st.markdown("<div class='sec-container'>", unsafe_allow_html=True)

        col_fp, col_ca = st.columns(2)

        with col_fp:
            st.markdown("<div class='sec-btn'>", unsafe_allow_html=True)
            if st.button("Forgot Password?"):
                navigate("Forgot")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_ca:
            st.markdown("<div class='sec-btn'>", unsafe_allow_html=True)
            if st.button("Create Account"):
                navigate("Signup")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
