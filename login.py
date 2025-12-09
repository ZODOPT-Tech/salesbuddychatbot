import streamlit as st
from PIL import Image
import requests
from io import BytesIO

LOGO_URL = "https://raw.githubusercontent.com/ZODOPT-Tech/Wheelbrand/main/images/zodopt.png"
PRIMARY_COLOR = "#0B2A63"


# ---------------- STYLES ----------------
def apply_styles():
    st.markdown(f"""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {{
        font-family: "Inter", sans-serif;
        background-color: #F6F8FB;
    }}

    [data-testid="stHeader"] {{
        background: transparent;
    }}

    .left-panel {{
        text-align: center;
        padding-top: 60px;
    }}

    .contact {{
        margin-top: 35px;
        font-size: 17px;
        font-weight: 500;
        line-height: 2.2;
        width: 350px;
        text-align: left;
        margin-left: auto;
        margin-right: auto;
    }}

    .title {{
        font-size: 36px;
        font-weight: 800;
        margin-bottom: 38px;
        margin-top: 70px;
        color: {PRIMARY_COLOR};
    }}

    .stTextInput label {{
        font-weight: 600 !important;
        font-size: 16px !important;
        margin-bottom: 6px !important;
        color: #1A1F36 !important;
    }}

    .stTextInput input {{
        height: 50px !important;
        border-radius: 8px !important;
        border: 1px solid #CBD5E0 !important;
        font-size: 16px !important;
        padding-left: 12px !important;
        background: white !important;
    }}

    /* LOGIN FULL WIDTH BUTTON */
    .login-full button,
    .login-full button span {{
        background-color: {PRIMARY_COLOR} !important;
        color: white !important;
        width: 100% !important;
        height: 55px !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: none !important;
        margin-top: 10px !important;
    }}

    /* SIDE BY SIDE BUTTONS */
    .btn-row {{
        display: flex;
        justify-content: center;
        gap: 36px;
        margin-top: 32px;
    }}

    .btn-row button,
    .btn-row button span {{
        background-color: {PRIMARY_COLOR} !important;
        color: white !important;
        width: 260px !important;
        height: 52px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: none !important;
    }}

    button:hover {{
        opacity: 0.92 !important;
    }}

    </style>
    """, unsafe_allow_html=True)


# ---------------- UI ----------------
def render(navigate):
    st.set_page_config(layout="wide")
    apply_styles()

    left, right = st.columns([1.1, 1.2])

    # LEFT CONTENT
    with left:
        st.markdown("<div class='left-panel'>", unsafe_allow_html=True)

        try:
            logo = Image.open(BytesIO(requests.get(LOGO_URL).content))
            st.image(logo, width=330)
        except:
            st.write("Logo failed")

        st.markdown("""
        <div class="contact">
        📞 Phone: +123-456-7890  
        ✉️ Email: hello@vclarifi.com  
        🌐 Website: www.vclarifi.com  
        📍 India
        </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


    # RIGHT CONTENT
    with right:
        st.markdown("<div class='title'>LOGIN TO YOUR ACCOUNT</div>", unsafe_allow_html=True)

        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")

        # LOGIN FULL WIDTH
        st.markdown("<div class='login-full'>", unsafe_allow_html=True)
        if st.button("Login", key="login_main"):
            navigate("Dashboard")
        st.markdown("</div>", unsafe_allow_html=True)

        # TWO SMALL BUTTONS
        st.markdown("<div class='btn-row'>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Forgot Password?", key="forgot"):
                navigate("Forgot")

        with col2:
            if st.button("Create Account", key="signup"):
                navigate("Signup")

        st.markdown("</div>", unsafe_allow_html=True)


# TESTING
if __name__ == "__main__":
    def dummy(p):
        st.success(f"→ {p}")
    render(dummy)
