import streamlit as st
import base64
from PIL import Image
import requests
from io import BytesIO


# --------- CONSTANTS ---------
BG_URL = "https://images.unsplash.com/photo-1503264116251-35a269479413?auto=format&fit=crop&w=1600&q=80"
LOGO_URL = "https://raw.githubusercontent.com/ZODOPT-Tech/Wheelbrand/main/images/zodopt.png"


# ---------- BACKGROUND + CSS ----------
def set_background(url):
    try:
        img_bytes = requests.get(url).content
        encoded = base64.b64encode(img_bytes).decode()

        st.markdown(
            f"""
            <style>
            [data-testid="stAppViewContainer"] {{
                background-image: url("data:image/jpeg;base64,{encoded}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
            }}

            [data-testid="stHeader"] {{
                background: rgba(0,0,0,0);
            }}

            .login-container {{
                background-color: rgba(255, 255, 255, 0.95);
                padding: 40px;
                border-radius: 20px;
                width: 400px;
                margin-top: 80px;
                box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2);
            }}

            .stButton>button {{
                width: 100%;
                padding: 15px;
                font-size: 18px;
                border-radius: 8px;
                background-color: #2c662d;
                color: white;
            }}

            .info {{
                color:white;
                font-size:14px;
                margin-top:20px;
                padding-left:60px;
                line-height:1.6;
            }}

            .inline {{
                display:flex;
                gap:16px;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except:
        pass


# ------------------ UI -------------------
def login(navigate_to):
    st.set_page_config(layout="wide")

    set_background(BG_URL)

    col_left, col_right = st.columns([1.2, 1])

    # LEFT PANEL
    with col_left:
        try:
            logo_bytes = requests.get(LOGO_URL).content
            logo = Image.open(BytesIO(logo_bytes))
            st.image(logo, width=300)
        except:
            st.error("Logo load failed")

        st.markdown(
            """
            <div class="info">
                <div class="inline">
                    <div><b>📞 Phone:</b> +123-456-7890</div>
                    <div><b>✉️ Email:</b> hello@vclarifi.com</div>
                </div>
                <div class="inline">
                    <div><b>🌐 Website:</b> www.vclarifi.com</div>
                    <div><b>📍 India</b></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # RIGHT PANEL
    with col_right:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:32px;font-weight:bold;color:navy;text-align:center;">LOGIN TO YOUR ACCOUNT</div>',
            unsafe_allow_html=True
        )

        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")

        if st.button("LOGIN"):
            st.success("Login UI working (no backend)")
            if navigate_to:
                navigate_to("Survey")

        st.markdown(
            """
            <div style="text-align:center;font-size:13px;color:#333;">
                Forgot Password?
                <a href="#" style="color:#007BFF;font-weight:bold;">Click here</a>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("Click here to Sign Up"):
            if navigate_to:
                navigate_to("User_Registration")

        st.markdown('</div>', unsafe_allow_html=True)


# ---------- Local testing ----------
if __name__ == "__main__":
    def dummy(page):
        st.success(f"NAVIGATION → {page}")
        st.stop()

    login(dummy)
