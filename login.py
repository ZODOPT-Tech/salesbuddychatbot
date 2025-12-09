import streamlit as st
import base64
import requests
from io import BytesIO
from PIL import Image


BG_URL = "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1600&q=80"
LOGO_URL = "https://raw.githubusercontent.com/ZODOPT-Tech/Wheelbrand/main/images/zodopt.png"


def set_background(url):
    img_bytes = requests.get(url).content
    encoded = base64.b64encode(img_bytes).decode()

    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpeg;base64,{encoded}");
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
    }}

    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
    }}

    .login-card {{
        background: rgba(255, 255, 255, 0.92);
        width: 480px;
        padding: 35px 40px;
        border-radius: 18px;
        box-shadow: 0 8px 22px rgba(0,0,0,0.25);
        margin-top: 60px;
    }}

    .contact {{
        margin-top: 40px;
        color: white;
        font-size: 16px;
        line-height: 1.8;
        font-weight: 500;
    }}

    .title {{
        font-size: 30px;
        font-weight: 800;
        text-align: center;
        color: #0a206c;
        margin-bottom: 28px;
    }}

    .stButton>button {{
        width: 100%;
        padding: 13px;
        border-radius: 8px;
        font-size: 18px;
        font-weight: 600;
        background: #1947e3;
        color: white;
        border: none;
    }}

    .link {{
        text-align:center;
        font-size:13px;
        margin-top:10px;
        color:#093682;
    }}

    .signup-btn>button {{
        width: 100%;
        padding: 13px;
        border-radius: 8px;
        font-size: 18px;
        font-weight: 600;
        background: #1a1a1a;
        color: white;
        border: none;
    }}
    </style>
    """, unsafe_allow_html=True)


def render(navigate_to):
    st.set_page_config(layout="wide")
    set_background(BG_URL)

    left, right = st.columns([1, 1])

    # LEFT SIDE
    with left:
        try:
            logo = Image.open(BytesIO(requests.get(LOGO_URL).content))
            st.image(logo, width=260)
        except:
            st.write("Logo error")

        st.markdown("""
        <div class="contact">
        📞 Phone: +123-456-7890 <br>
        ✉️ Email: hello@vclarifi.com <br>
        🌐 Website: www.vclarifi.com <br>
        📍 India
        </div>
        """, unsafe_allow_html=True)

    # RIGHT SIDE
    with right:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="title">LOGIN TO YOUR ACCOUNT</div>', unsafe_allow_html=True)

        email = st.text_input("Email Address")
        pwd = st.text_input("Password", type="password")

        if st.button("LOGIN"):
            st.success("UI Login working (no backend)")
            if navigate_to:
                navigate_to("Dashboard")

        st.markdown('<div class="link">Forgot Password?</div>', unsafe_allow_html=True)

        if st.button("Click here to Sign Up", key="signup", help="Create Account", use_container_width=True):
            if navigate_to:
                navigate_to("User_Registration")

        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    def test(p):
        st.write("NAVIGATE:", p)
    render(test)
