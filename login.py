import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import boto3
import json
import mysql.connector


# --------------------------------------------------------
# ---------------- AWS Secrets Manager -------------------
# --------------------------------------------------------
SECRET_ARN = "arn:aws:secretsmanager:ap-south-1:034362058776:secret:salesbuddy/secrets-0xh2TS"


@st.cache_resource
def get_db_secrets():
    """Fetch DB credentials from AWS Secrets Manager."""
    try:
        client = boto3.client("secretsmanager", region_name="ap-south-1")
        resp = client.get_secret_value(SecretId=SECRET_ARN)
        raw = json.loads(resp["SecretString"])
        return {
            "DB_HOST": raw["DB_HOST"],
            "DB_USER": raw["DB_USER"],
            "DB_PASSWORD": raw["DB_PASSWORD"],
            "DB_NAME": raw["DB_NAME"]
        }
    except Exception as e:
        st.error(f"Configuration Error: Failed to load DB secrets: {e}")
        st.stop()


@st.cache_resource
def get_conn():
    """Connect to MySQL using AWS secrets."""
    try:
        creds = get_db_secrets()
        conn = mysql.connector.connect(
            host=creds["DB_HOST"],
            user=creds["DB_USER"],
            password=creds["DB_PASSWORD"],
            database=creds["DB_NAME"],
            charset="utf8mb4"
        )
        return conn
    except mysql.connector.Error as e:
        st.error(f"Database Connection Error: {e}")
        st.stop()


# --------------------------------------------------------
# ---------------- AUTH LOGIC ----------------------------
# --------------------------------------------------------
def authenticate_user(email, password):
    """
    Validate login credentials against DB.
    """
    try:
        conn = get_conn()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT full_name, email
        FROM users
        WHERE email = %s AND password = %s
        LIMIT 1
        """
        cursor.execute(query, (email, password))
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if row:
            return True, row
        else:
            return False, None

    except Exception as e:
        st.error(f"Login failed: {e}")
        return False, None


# --------------------------------------------------------
# ---------------- CONSTANTS -----------------------------
# --------------------------------------------------------
LOGO_URL = "https://raw.githubusercontent.com/ZODOPT-Tech/Wheelbrand/main/images/zodopt.png"
PRIMARY_COLOR = "#0B2A63"


# --------------------------------------------------------
# ---------------- STYLES -------------------------------
# --------------------------------------------------------
def apply_styles():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {{
        font-family: "Inter", sans-serif;
        background-color: #F6F8FB;
    }}

    .stTextInput label {{
        display: block !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        color: #1A1F36 !important;
    }}

    .stTextInput input {{
        border-radius: 8px !important;
        height: 46px !important;
        border: 1px solid #CBD5E0 !important;
        background: white !important;
        font-size: 15px !important;
    }}

    div[data-testid="stVerticalBlock"] > div:first-child button,
    div[data-testid="stVerticalBlock"] > div:first-child button span {{
        background-color: {PRIMARY_COLOR} !important;
        color: white !important;
        height: 48px !important;
        font-size: 17px !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
    }}

    .sec-container button,
    .sec-container button span {{
        background-color: {PRIMARY_COLOR} !important;
        color: white !important;
        width: 200px !important;
        height: 44px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }}

    button:hover {{
        opacity: 0.92 !important;
    }}

    .title {{
        font-size: 34px;
        font-weight: 800;
        margin-bottom: 32px;
        margin-top: 80px;
        color: {PRIMARY_COLOR};
        text-align:left;
    }}

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

    .sec-container {{
        display: flex;
        justify-content: center;
        gap: 28px;
        margin-top: 20px;
    }}
    </style>
    """, unsafe_allow_html=True)


# --------------------------------------------------------
# ---------------- PAGE CONTENT --------------------------
# --------------------------------------------------------
def render(navigate):
    st.set_page_config(layout="wide")
    apply_styles()

    left, right = st.columns([1.1, 1])

    # LEFT PANEL
    with left:
        st.markdown("<div class='left-panel'>", unsafe_allow_html=True)

        try:
            response = requests.get(LOGO_URL)
            response.raise_for_status()
            logo = Image.open(BytesIO(response.content))
            st.image(logo, width=330)
        except Exception:
            st.error("Logo loading failed")

        st.markdown("""
        <div class="contact">
        📞 Phone: +91 8647878785 <br>
        ✉️ Email: enquiry@zodopt.com <br>
        🌐 Website: www.zodopt.com <br>
        📍 Location : Bengaluru
        </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # RIGHT PANEL
    with right:
        st.markdown("<div class='title'>LOGIN TO YOUR ACCOUNT</div>", unsafe_allow_html=True)

        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            success, user_data = authenticate_user(email, password)

            if success:
                st.session_state.logged_in = True
                st.session_state.user_data = user_data
                navigate("chatbot")
            else:
                st.error("Invalid Email or Password")

        st.markdown("<div class='sec-container'>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Forgot Password?", key="forgot_btn"):
                navigate("forgot_password")

        with col2:
            if st.button("Create Account", key="create_btn"):
                navigate("signup")

        st.markdown("</div>", unsafe_allow_html=True)


# --------------------------------------------------------
# ---------------- TESTING -------------------------------
# --------------------------------------------------------
if __name__ == "__main__":
    def dummy_nav(x):
        st.success(f"Navigate → {x}")
    render(dummy_nav)
