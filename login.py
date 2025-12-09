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
        background-color: #F7F9FC;
        color: #1D1F23;
    }

    [data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }

    .left-panel {
        text-align: center;
        margin-top: 80px;
    }

    .details {
        margin-top: 35px;
        line-height: 2.0;
        font-size: 16px;
        font-weight: 500;
        color: #2A2E35;
    }

    .login-card {
        width: 400px;
        margin: auto;
        margin-top: 100px;
        padding: 35px 32px;
        background: white;
        border-radius: 14px;
        box-shadow: 0px 6px 18px rgba(0,0,0,0.08);
    }

    .title {
        font-size: 26px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 28px;
        color: #062B5C;
    }

    .stTextInput > div > div > input {
        border-radius: 8px;
        height: 42px;
        font-size: 15px;
        font-weight: 500;
        background-color: #F0F3F7;
        border: 1px solid #D6DAE2;
    }

    .login-btn > button {
        width: 100%;
        height: 42px;
        background-color: #062B5C;
        border-radius: 8px;
        border: none;
        color: white;
        font-weight: 700;
        font-size: 16px;
    }

    .bottom-links {
        display: flex;
        justify-content: space-between;
        margin-top: 18px;
        font-size: 14px;
        font-weight: 600;
    }

    .link {
        color: #1E5FBF;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)


def render(navigate):
    st.set_page_config(layout="wide")

    apply_styles()

    left, right = st.columns([1, 1])

    # LEFT SIDE
    with left:
        st.markdown("<div class='left-panel'>", unsafe_allow_html=True)
        try:
            logo = Image.open(BytesIO(requests.get(LOGO_URL).content))
            st.image(logo, width=280)
        except:
            st.write("Logo load error")

        st.markdown("""
        <div class='details'>
        📞 Phone: +123-456-7890 <br>
        ✉️ Email: hello@vclarifi.com <br>
        🌐 Website: www.vclarifi.com <br>
        📍 India
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # RIGHT SIDE
    with right:
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)

        st.markdown("<div class='title'>LOGIN TO YOUR ACCOUNT</div>", unsafe_allow_html=True)

        email = st.text_input("Email Address")
        pwd = st.text_input("Password", type="password")

        st.markdown("<div class='login-btn'>", unsafe_allow_html=True)
        if st.button("Login"):
            navigate("Dashboard")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='bottom-links'>", unsafe_allow_html=True)

        if st.button("Forgot Password?", key="forgot"):
            navigate("Forgot")

        if st.button("Create Account", key="signup"):
            navigate("Signup")

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    def test(page):
        st.write("Navigate to:", page)
    render(test)
