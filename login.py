import streamlit as st
import mysql.connector
import bcrypt
import boto3
import json

# -------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------
st.set_page_config(page_title="Sales Buddy Login", layout="wide")

# -------------------------------------------------------
# CSS
# -------------------------------------------------------
CSS = """
<style>

* {
    font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Remove default Streamlit padding so we can control everything */
.stApp > header {display: none;}
.stApp > main .block-container {
    padding: 0 !important;
    margin: 0 !important;
}

/* Wrapper for the whole page */
.page-wrapper {
    height: 100vh;
    width: 100vw;
}

/* Make the columns stretch full height */
.page-wrapper [data-testid="stHorizontalBlock"] {
    height: 100%;
}

/* LEFT PANEL */
.left-panel {
    height: 100%;
    padding: 60px 80px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    background-color: #ffffff;
}

.logo-text {
    font-size: 26px;
    font-weight: 700;
    color: #1a1f2b;
    margin-bottom: 40px;
}

.main-heading {
    font-size: 42px;
    font-weight: 800;
    color: #151821;
    margin-bottom: 8px;
}

.subtext {
    font-size: 18px;
    color: #7d8a96;
    margin-bottom: 35px;
}

/* Input styling */
.stTextInput > div > div > input {
    background: #eef3f6 !important;
    border-radius: 14px !important;
    border: none !important;
    padding: 16px !important;
    font-size: 17px !important;
}

.stTextInput input::placeholder {
    color: #9ca3af;
}

/* Login button (submit inside form) */
.left-panel form button {
    background: linear-gradient(90deg,#27c4a8,#23a6d5) !important;
    border-radius: 30px !important;
    border: none !important;
    padding: 14px 0 !important;
    margin-top: 22px !important;
    width: 100% !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    color: #ffffff !important;
}

/* RIGHT PANEL */
.right-panel {
    height: 100%;
    padding: 60px 50px;
    background: linear-gradient(180deg,#27c4a8,#23a6d5);
    color: #ffffff;
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: center;
    text-align: left;
}

/* Abstract circles like the design */
.right-panel::before {
    content: "";
    position: absolute;
    top: 10%;
    right: -40px;
    width: 220px;
    height: 220px;
    background: rgba(255,255,255,0.12);
    border-radius: 50%;
}

.right-panel::after {
    content: "";
    position: absolute;
    bottom: -60px;
    left: -40px;
    width: 280px;
    height: 280px;
    background: rgba(255,255,255,0.12);
    border-radius: 50%;
}

.side-title {
    font-size: 40px;
    font-weight: 800;
    margin-bottom: 16px;
    position: relative;
    z-index: 1;
}

.side-text {
    font-size: 18px;
    color: #e5fbf7;
    margin-bottom: 40px;
    position: relative;
    z-index: 1;
}

/* Sign up button on right side */
.right-panel .stButton > button {
    background: #ffffff !important;
    color: #21b5a2 !important;
    border-radius: 30px !important;
    padding: 14px 40px !important;
    border: none !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    position: relative;
    z-index: 1;
}

</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# -------------------------------------------------------
# SECRETS / DB
# -------------------------------------------------------
SECRET_ARN = "arn:aws:secretsmanager:ap-south-1:034362058776:secret:salesbuddy/secrets-0xh2TS"

@st.cache_resource
def get_db_secrets():
    client = boto3.client("secretsmanager", region_name="ap-south-1")
    resp = client.get_secret_value(SecretId=SECRET_ARN)
    return json.loads(resp["SecretString"])

@st.cache_resource
def get_conn():
    creds = get_db_secrets()
    return mysql.connector.connect(
        host=creds["DB_HOST"],
        user=creds["DB_USER"],
        password=creds["DB_PASSWORD"],
        database=creds["DB_NAME"],
        charset="utf8mb4"
    )

# -------------------------------------------------------
# RENDER FUNCTION
# -------------------------------------------------------
def render(navigate):

    # Outer wrapper (forces full screen, no scroll on normal displays)
    st.markdown("<div class='page-wrapper'>", unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2], gap="none")

    # ---------------- LEFT PANEL (LOGIN) ----------------
    with col_left:
        st.markdown("<div class='left-panel'>", unsafe_allow_html=True)

        st.markdown("<div class='logo-text'>Sales Buddy</div>", unsafe_allow_html=True)
        st.markdown("<div class='main-heading'>Login to Your Account</div>", unsafe_allow_html=True)
        st.markdown("<div class='subtext'>Access your account</div>", unsafe_allow_html=True)

        with st.form("login_form"):
            email = st.text_input("Email", placeholder="Email")
            password = st.text_input("Password", type="password", placeholder="Password")
            submitted = st.form_submit_button("Sign In")

            if submitted:
                if not email or not password:
                    st.error("Please enter both email and password.")
                else:
                    try:
                        conn = get_conn()
                        cur = conn.cursor(dictionary=True)
                        cur.execute(
                            "SELECT user_id, full_name, email, company, password "
                            "FROM users WHERE email=%s",
                            (email,)
                        )
                        user = cur.fetchone()
                        cur.close()

                        if user and bcrypt.checkpw(
                            password.encode("utf-8"),
                            user["password"].encode("utf-8")
                        ):
                            st.session_state.logged_in = True
                            st.session_state.user_data = {
                                "user_id": user["user_id"],
                                "full_name": user["full_name"],
                                "email": user["email"],
                                "company": user["company"],
                            }
                            navigate("chatbot")
                        else:
                            st.error("Incorrect email or password.")
                    except Exception as e:
                        st.error(f"Login failed: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- RIGHT PANEL (NEW HERE) ----------------
    with col_right:
        st.markdown("<div class='right-panel'>", unsafe_allow_html=True)

        st.markdown("<div class='side-title'>New Here?</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='side-text'>"
            "Sign up and discover a great amount of new opportunities!"
            "</div>",
            unsafe_allow_html=True,
        )

        if st.button("Sign Up", key="signup_btn"):
            navigate("signup")

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
