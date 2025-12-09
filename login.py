import streamlit as st
import base64
import requests
from io import BytesIO
from PIL import Image

LOGO_URL = "https://raw.githubusercontent.com/ZODOPT-Tech/Wheelbrand/main/images/zodopt.png"
BG_URL = "https://images.unsplash.com/photo-1526401281623-c3e51775f7c5?auto=format&fit=crop&w=1600&q=80"


def set_background(url):
    img_bytes = requests.get(url).content
    encoded = base64.b64encode(img_bytes).decode()

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');

    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Poppins', sans-serif;
        background-image: url("data:image/jpeg;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    /* remove default header */
    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
    }}

    /* Login card glass effect */
    .card {{
        width: 450px;
        padding: 40px;
        background: rgba(255,255,255,0.18);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        margin-top: 80px;
    }}

    .title {{
        font-size: 32px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 30px;
        color: #001b64;
    }}

    label {{
        color: #001b64 !important;
        font-weight: 600;
    }}

    .stTextInput>div>div>input {{
        border-radius: 10px;
        padding: 12px;
        background: rgba(255,255,255,0.86);
    }}

    .primary-btn>button {{
        width: 100%;
        padding: 14px;
        border-radius: 12px;
        border: none;
        font-weight: 700;
        font-size: 18px;
        background: linear-gradient(135deg,#0066ff,#0028a4);
        color: white;
    }}

    .secondary-btn>button {{
        width: 100%;
        padding: 12px;
        border-radius: 12px;
        margin-top: 10px;
        background: rgba(0,0,0,0.75);
        color: white;
        border: none;
        font-size: 17px;
        font-weight: 600;
    }}

    .link {{
        text-align:center;
        margin-top:10px;
        color:#0035c8;
        font-size: 14px;
        cursor:pointer;
        font-weight:500;
    }}

    .contact {{
        margin-top:60px;
        font-size:17px;
        line-height:1.8;
        color: white;
        font-weight:400;
    }}
    </style>
    """, unsafe_allow_html=True)


def render(navigate):
    st.set_page_config(layout="wide")

    set_background(BG_URL)

    col1, col2 = st.columns([1,1])

    # LEFT PANEL
    with col1:
        try:
            logo = Image.open(BytesIO(requests.get(LOGO_URL).content))
            st.image(logo, width=300)
        except:
            st.write("Logo load error")

        st.markdown("""
        <div class="contact">
        📞 Phone: +123-456-7890 <br>
        ✉️ Email: hello@vclarifi.com <br>
        🌐 Website: www.vclarifi.com <br>
        📍 India
        </div>
        """, unsafe_allow_html=True)

    # RIGHT PANEL
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="title">LOGIN TO YOUR ACCOUNT</div>', unsafe_allow_html=True)

        email = st.text_input("Email Address")
        pwd = st.text_input("Password", type="password")

        if st.button("Login", key="login", help="Login", use_container_width=True):
            st.success("UI only — login working")
            navigate("Dashboard")

        st.markdown('<div class="link" onclick="window.location.href=\'#\'">Forgot Password?</div>', unsafe_allow_html=True)

        if st.button("Create a new account", key="signup", use_container_width=True):
            navigate("Signup")

        st.markdown('</div>', unsafe_allow_html=True)
