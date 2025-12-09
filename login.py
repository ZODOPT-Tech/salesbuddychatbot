import streamlit as st
import mysql.connector
import bcrypt
import boto3
import json

# --------------------------------------------
# PAGE CONFIG
# --------------------------------------------
st.set_page_config(page_title="Sales Buddy | Login", layout="wide")


# --------------------------------------------
# CSS
# --------------------------------------------
CSS = """
<style>

* {
    font-family: "Inter", sans-serif;
}

.stApp > header, .stApp > footer {
    display: none;
}

.stApp > main .block-container {
    padding: 0 !important;
    margin: 0 !important;
}

.page-wrapper {
    width: 100vw;
    height: 100vh;
    overflow: hidden;
}

/* Full height columns */
[data-testid="stHorizontalBlock"] {
    height: 100%;
}

/* LEFT: LOGIN PANEL */
.left-panel {
    background: #ffffff;
    height: 100%;
    padding: 60px 80px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.main-heading {
    font-size: 42px;
    font-weight: 800;
    color: #111318;
    margin-bottom: 10px;
}

.subtext {
    font-size: 18px;
    color: #7a8996;
    margin-bottom: 30px;
}

/* Login card container */
.form-wrapper {
    background: #ffffff;
    padding: 32px;
    border-radius: 14px;
    border: 1px solid #e5e7eb;
    max-width: 480px;
}

/* Input */
.stTextInput > div > div > input {
    background: #eef2f6 !important;
    border-radius: 12px !important;
    border: none !important;
    padding: 14px !important;
    font-size: 16px !important;
}

.stTextInput input::placeholder {
    color: #9da5af;
}

/* Button */
form button {
    background: linear-gradient(90deg,#27c4a7,#24a7d4) !important;
    border-radius: 30px !important;
    padding: 14px 0 !important;
    font-size: 17px !important;
    font-weight: 700 !important;
    border: none !important;
    width: 100% !important;
    margin-top: 12px;
    color: #ffffff !important;
}


/* RIGHT PANEL = SALES BUDDY SIDE */
.right-panel {
    height: 100%;
    position: relative;
    color: #ffffff;
    padding: 70px 80px;
    background: linear-gradient(180deg,#27c4a8,#23a6d5);
    display: flex;
    flex-direction: column;
    justify-content: center;
    text-align: left;
}

/* Circles */
.right-panel::before {
    content:"";
    position:absolute;
    top: 12%;
    right: -40px;
    width: 200px;
    height: 200px;
    background: rgba(255,255,255,0.13);
    border-radius:50%;
}

.right-panel::after {
    content:"";
    position:absolute;
    bottom: -50px;
    left: -70px;
    width: 280px;
    height: 280px;
    background: rgba(255,255,255,0.12);
    border-radius:50%;
}

/* Branding Title */
.brand-title {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 35px;
    position:relative;
    z-index:10;
}

/* New Here title */
.side-title {
    font-size: 40px;
    font-weight: 900;
    margin-bottom: 14px;
    position:relative;
    z-index:10;
}

.side-text {
    font-size: 18px;
    color: #e6fbf7;
    margin-bottom: 35px;
    position:relative;
    z-index:10;
}

.right-panel .stButton > button {
    background: #ffffff !important;
    color: #22b5a1 !important;
    border-radius: 30px !important;
    padding: 14px 38px !important;
    font-size: 17px !important;
    font-weight: 700 !important;
    border: none !important;
    position:relative;
    z-index:10;
}

</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# --------------------------------------------
# AWS Secrets & DB
# --------------------------------------------
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


# --------------------------------------------
# RENDER
# --------------------------------------------
def render(navigate):

    st.markdown("<div class='page-wrapper'>", unsafe_allow_html=True)

    col_left, col_right = st.columns([3,2], gap="small")


    # LEFT = Login Section
    with col_left:
        st.markdown("<div class='left-panel'>", unsafe_allow_html=True)

        st.markdown("<div class='main-heading'>Login to Your Account</div>", unsafe_allow_html=True)
        st.markdown("<div class='subtext'>Access your account</div>", unsafe_allow_html=True)

        st.markdown("<div class='form-wrapper'>", unsafe_allow_html=True)

        with st.form("login_form"):
            email = st.text_input("", placeholder="Email")
            password = st.text_input("", type="password", placeholder="Password")
            pressed = st.form_submit_button("Sign In")

            if pressed:
                conn = get_conn()
                cur = conn.cursor(dictionary=True)
                cur.execute("SELECT user_id, full_name, email, company, password FROM users WHERE email=%s", (email,))
                user = cur.fetchone()
                cur.close()

                if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                    st.session_state.logged_in = True
                    st.session_state.user_data = user
                    navigate("chatbot")
                else:
                    st.error("Incorrect email or password.")

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


    # RIGHT = Branding + Sign Up
    with col_right:
        st.markdown("<div class='right-panel'>", unsafe_allow_html=True)

        st.markdown("<div class='brand-title'>Sales Buddy</div>", unsafe_allow_html=True)
        st.markdown("<div class='side-title'>New Here?</div>", unsafe_allow_html=True)
        st.markdown("<div class='side-text'>Sign up and discover a great amount of new opportunities!</div>", unsafe_allow_html=True)

        if st.button("Sign Up"):
            navigate("signup")

        st.markdown("</div>", unsafe_allow_html=True)


    st.markdown("</div>", unsafe_allow_html=True)
