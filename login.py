import streamlit as st
import base64
import requests
from io import BytesIO
from PIL import Image

LOGO_URL = "https://raw.githubusercontent.com/ZODOPT-Tech/Wheelbrand/main/images/zodopt.png"
BG_URL = "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=1600&q=80"


def set_styles(bg):
    bg_bytes = requests.get(bg).content
    encoded_bg = base64.b64encode(bg_bytes).decode()

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Inter', sans-serif;
        background-image: url("data:image/jpeg;base64,{encoded_bg}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        color: #0E1A2A;
    }}

    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
    }}

    .login-card {{
        width: 420px;
        margin: auto;
        margin-top: 85px;
        padding: 45px 40px;
        border-radius: 18px;
        background: rgba(255,255,255,0.16);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        box-shadow: 0px 8px 28px rgba(0,0,0,0.18);
    }}

    .title {{
        font-size: 28px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 35px;
        color: #0E1A2A;
    }}

    .stTextInput>div>div>input {{
        border-radius: 10px;
        height: 48px;
        font-size: 16px;
        font-weight: 500;
        border: 1px solid #C8CFD9;
        background: rgba(255,255,255,0.80);
    }}

    .login-btn>button {{
        border-radius: 10px;
        height: 48px;
        font-size: 17px;
        font-weight: 700;
        width: 100%;
        border: none;
        color: white;
        background: linear-gradient(135deg,#1E5FBF,#003AAE);
    }}

    .actions {{
        display: flex;
        justify-content: space-between;
        margin-top: 18px;
        font-weight: 600;
        font-size: 15px;
    }}

    .link-action {{
        color: #1E5FBF;
        cursor: pointer;
    }}

    .contact {{
        margin-top: 45px;
        line-height: 2.0;
        font-size: 17px;
        font-weight: 400;
        color: #0E1A2A;
    }}

    .contact-line {{
        display: flex;
        gap: 12px;
        align-items: center;
    }}
    </style>
    """, unsafe_allow_html=True)


def render(navigate):
    st.set_page_config(layout="wide")
    set_styles(BG_URL)

    col1, col2 = st.columns([1, 1], gap="large")

    # LEFT SIDE (Brand)
    with col1:
        try:
            logo = Image.open(BytesIO(requests.get(LOGO_URL).content))
            st.image(logo, width=300)
        except:
            st.write("Logo load error")

        st.markdown("""
        <div class="contact">
            <div class="contact-line">📞 Phone: +123-456-7890</div>
            <div class="contact-line">✉️ Email: hello@vclarifi.com</div>
            <div class="contact-line">🌐 Website: www.vclarifi.com</div>
            <div class="contact-line">📍 India</div>
        </div>
        """, unsafe_allow_html=True)

    # RIGHT SIDE (Form)
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="title">LOGIN TO YOUR ACCOUNT</div>', unsafe_allow_html=True)

        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")

        st.markdown('<div class="login-btn">', unsafe_allow_html=True)
        if st.button("Login"):
            navigate("Dashboard")
        st.markdown('</div>', unsafe_allow_html=True)

        # Inline Actions
        st.markdown('<div class="actions">', unsafe_allow_html=True)

        if st.button("Forgot Password?", key="forgot", help="Recover Account"):
            navigate("Forgot")

        if st.button("Create Account", key="signup", help="Register Now"):
            navigate("Signup")

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
