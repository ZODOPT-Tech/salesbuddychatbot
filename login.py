import streamlit as st
from PIL import Image
import requests
from io import BytesIO

# ---------------- CONSTANTS ----------------
LOGO_URL = "https://raw.githubusercontent.com/ZODOPT-Tech/Wheelbrand/main/images/zodopt.png"
PRIMARY_COLOR = "#0B2A63"


# ---------------- STYLES ----------------
def apply_styles():
    st.markdown(f"""
    <style>

    /* GLOBAL FONT */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {{
        font-family: "Inter", sans-serif;
        background-color: #F6F8FB;
    }}

    [data-testid="stHeader"] {{
        background: transparent;
    }}

    /* INPUT LABEL FIX */
    .stTextInput label {{
        display: block !important;
        margin-bottom: 6px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        color: #1A1F36 !important;
    }}

    /* INPUT FIELD */
    .stTextInput input {{
        border-radius: 8px !important;
        height: 46px !important;
        border: 1px solid #CBD5E0 !important;
        background: white !important;
        font-size: 15px !important;
    }}

    /* -------- BUTTON FIXES -------- */

    /* Primary Login Button: Use Streamlit default styling (no custom CSS applied here) */
    /* To ensure it stays small and white as in the image, we rely on the default Streamlit theme */
    
    /* SECONDARY BUTTONS (Forgot + Create) */
    /* Target the buttons within the .sec-container and .sec-col-btn wrappers to apply custom style */
    .sec-col-btn button {{
        background-color: {PRIMARY_COLOR} !important;
        color: white !important;
        width: 100% !important; /* Forces them to take the full width of their respective columns */
        height: 44px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        border: none !important;
    }}

    /* Remove default hover */
    button:hover {{
        opacity: 0.92 !important;
    }}

    /* TITLE */
    .title {{
        font-size: 34px;
        font-weight: 800;
        margin-bottom: 32px;
        margin-top: 80px;
        color: {PRIMARY_COLOR};
        text-align:left;
    }}

    /* LEFT SIDE */
    .left-panel {{
        text-align: center;
        padding-top: 80px;
    }}

    .contact {{
        margin-top: 35px;
        font-size: 16px;
        font-weight: 500;
        line-height: 2.2;
        width: 330px;
        margin-left: auto;
        margin-right: auto;
        text-align:left;
    }}

    /* Secondary button wrapper for spacing - now we don't need a custom flex container, 
       st.columns will handle the layout based on the final image.
       However, we keep the original sec-container class for structure if needed later. */
    .sec-container {{
        margin-top: 20px;
    }}

    </style>
    """, unsafe_allow_html=True)


# ---------------- PAGE CONTENT ----------------
def render(navigate):
    st.set_page_config(layout="wide")
    apply_styles()

    left, right = st.columns([1.1, 1])

    # LEFT
    with left:
        st.markdown("<div class='left-panel'>", unsafe_allow_html=True)

        try:
            # Fetch and display logo
            response = requests.get(LOGO_URL)
            response.raise_for_status() 
            logo = Image.open(BytesIO(response.content))
            st.image(logo, width=330)
        except Exception as e:
            st.error(f"Logo failed to load: {e}")

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

        # Primary Button: Uses Streamlit default styling (small, white)
        if st.button("Login"):
            navigate("Dashboard")

        # Secondary Button Container: Uses st.columns to spread buttons across the width
        st.markdown("<div class='sec-container'>", unsafe_allow_html=True)

        # Use two columns for 'Forgot Password' and 'Create Account'
        sec_col1, sec_col2 = st.columns(2) 

        with sec_col1:
            st.markdown("<div class='sec-col-btn'>", unsafe_allow_html=True)
            if st.button("Forgot Password?", key="forgot_btn"): 
                navigate("Forgot")
            st.markdown("</div>", unsafe_allow_html=True)


        with sec_col2:
            st.markdown("<div class='sec-col-btn'>", unsafe_allow_html=True)
            if st.button("Create Account", key="create_btn"): 
                navigate("Signup")
            st.markdown("</div>", unsafe_allow_html=True)


        st.markdown("</div>", unsafe_allow_html=True)


# ---------------- TESTING ----------------
if __name__ == "__main__":
    def dummy_nav(x): st.success(f"Navigate → {x}")
    render(dummy_nav)
