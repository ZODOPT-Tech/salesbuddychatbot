import streamlit as st
import base64
import requests
from io import BytesIO
from PIL import Image

LOGO_URL = "https://raw.githubusercontent.com/ZODOPT-Tech/Wheelbrand/main/images/zodopt.png"
BG_URL = "https://images.unsplash.com/photo-1526401281623-c3e51775f7c5?auto=format&fit=crop&w=1600&q=80"


def set_background(url):
    bg_bytes = requests.get(url).content
    encoded = base64.b64encode(bg_bytes).decode()

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Poppins', sans-serif;
        background-image: url("data:image/jpeg;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
    }}

    .login-card {{
        width: 430px;
        background: rgba(255,255,255,0.16);
        backdrop-filter: blur(14px);
        border-radius: 18px;
        padding: 35px 38px;
        margin-top: 75px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }}

    .title {{
        font-size: 28px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 30px;
        color: #062B5C;
    }}

    .stTextInput>div>div>input {{
        border-radius: 10px;
        padding: 11px;
        background: rgba(255,255,255,0.88);
        font-weight: 500;
        border: 1px solid #d2d6e0;
        color: #0D1A2F;
    }}

    .login-btn>button {{
        width: 100%;
        padding: 13px;
        background: #0059FF;
        border-radius: 10px;
        color: white;
        font-size: 17px;
        font-weight: 600;
        border: none;
    }}

    .inline-links {{
        display: flex;
        justify-content: space-between;
        margin-top: 15px;
    }}

    .link-btn {{
        font-size: 15px;
        font-weight: 600;
        color: #0059FF;
        cursor: pointer;
    }}

    .contact {{
        margin-top: 40px;
        line-height: 1.9;
        font-size: 17px;
        color: white;
        font-weight: 400;
    }}

    .contact-line {{
        display: flex;
        gap: 10px;
        align-items: center;
    }}
    </style>
    """, unsafe_allow_html=True)


def render(navigate):
    st.set_page_config(layout="wide")

    set_background(BG_URL)

    left, right = st.columns([1,1])

    # LEFT SECTION (Branding + Contact)
    with left:
        try:
            logo = Image.open(BytesIO(requests.get(LOGO_URL).content))
            st.image(logo, width=300)
        except:
            st.write("Logo load error")

        st.markdown("""
        <div class="contact">
            <div class="contact-line">📞  +123-456-7890</div>
            <div class="contact-line">✉️  hello@vclarifi.com</div>
            <div class="contact-line">🌐  www.vclarifi.com</div>
            <div class="contact-line">📍  India</div>
        </div>
        """, unsafe_allow_html=True)

    # RIGHT SECTION (Login)
    with right:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="title">LOGIN TO YOUR ACCOUNT</div>', unsafe_allow_html=True)

        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")

        # Login button
        st.markdown('<div class="login-btn">', unsafe_allow_html=True)
        if st.button("Login"):
            navigate("Dashboard")
        st.markdown('</div>', unsafe_allow_html=True)

        # Inline actions (same line)
        st.markdown('<div class="inline-links">', unsafe_allow_html=True)

        if st.button("Forgot Password?", key="forgot"):
            navigate("Forgot")

        if st.button("Create Account", key="signup"):
            navigate("Signup")

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    def test(page):
        st.write("Navigate:", page)
    render(test)
