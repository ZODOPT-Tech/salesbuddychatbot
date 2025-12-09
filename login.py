import streamlit as st
import mysql.connector
import bcrypt
import boto3
import json

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(page_title="Sales Buddy | Login", layout="wide")


# ---------------------------------------------------
# GLOBAL CSS
# ---------------------------------------------------
CSS = """
<style>

* {
    font-family: "Inter", sans-serif;
}

.stApp > header, .stApp > footer {display:none;}

.stApp > main .block-container {
    padding: 0 !important;
    margin: 0 !important;
}

/* Full page wrapper */
.page-wrapper {
    width: 100vw;
    height: 100vh;
    overflow: hidden;
}

/* Columns fill height */
[data-testid="stHorizontalBlock"] {
    height: 100%;
}

/* LEFT PANEL */
.left-panel {
    background: #ffffff;
    padding: 60px 90px;
    height: 100%;
    display: flex;
    flex-direction:column;
    justify-content:center;
}

.title {
    font-size: 46px;
    font-weight: 900;
    color: #14161c;
    margin-bottom: 8px;
}

.subtitle {
    font-size:19px;
    color:#7b8592;
    margin-bottom: 40px;
}

/* Form container (card) */
.form-card {
    background:#ffffff;
    padding: 30px;
    border-radius: 14px;
    border: 1px solid #e2e4e8;
    max-width: 450px;
}

/* Input */
.stTextInput > div > div > input {
    background:#eef2f6 !important;
    border-radius:12px !important;
    border:none !important;
    padding:14px !important;
    font-size:17px !important;
}

/* Button */
form button {
    background:linear-gradient(90deg,#27c4a8,#23a6d5) !important;
    border-radius:30px !important;
    padding:14px 0 !important;
    width:100% !important;
    border:none !important;
    font-size:17px !important;
    font-weight:700 !important;
    color:#ffffff !important;
    margin-top:12px !important;
}


/* RIGHT PANEL (FULL COLUMN) */
.right-panel {
    height:100%;
    padding:80px 60px;
    background:linear-gradient(180deg,#27c4a8,#23a6d5);
    color:white;
    display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:flex-start;
    position: relative;
}

/* Abstract circles */
.right-panel::before {
    content:"";
    position:absolute;
    right:-50px;
    top:120px;
    width:260px;
    height:260px;
    background:rgba(255,255,255,0.12);
    border-radius:50%;
    z-index:1;
}

.right-panel::after {
    content:"";
    position:absolute;
    left:-70px;
    bottom:-80px;
    width:300px;
    height:300px;
    background:rgba(255,255,255,0.11);
    border-radius:50%;
    z-index:1;
}

/* Branding */
.brand {
    font-size:28px;
    font-weight:700;
    margin-bottom:40px;
    position:relative;
    z-index:10;
}

.side-title {
    font-size:44px;
    font-weight:900;
    margin-bottom:14px;
    position:relative;
    z-index:10;
}

.side-text {
    font-size:19px;
    line-height:1.4;
    max-width:350px;
    margin-bottom:35px;
    color:#e6fbf7;
    position:relative;
    z-index:10;
}

.right-panel .stButton > button {
    background:#ffffff !important;
    color:#20b5a1 !important;
    border-radius:30px !important;
    padding:14px 40px !important;
    font-size:17px !important;
    font-weight:700 !important;
    border:none !important;
    position:relative;
    z-index:10;
}

</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------
# AWS Secrets & DB
# ---------------------------------------------------
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
        database=creds["DB_NAME"]
    )


# ---------------------------------------------------
# UI RENDER
# ---------------------------------------------------
def render(navigate):

    st.markdown("<div class='page-wrapper'>", unsafe_allow_html=True)

    left, right = st.columns([3,2], gap="none")


    # LEFT SIDE
    with left:
        st.markdown("<div class='left-panel'>", unsafe_allow_html=True)

        st.markdown("<div class='title'>Login to Your Account</div>", unsafe_allow_html=True)
        st.markdown("<div class='subtitle'>Access your account</div>", unsafe_allow_html=True)

        st.markdown("<div class='form-card'>", unsafe_allow_html=True)

        with st.form("login_form"):
            email = st.text_input("", placeholder="Email")
            password = st.text_input("", type="password", placeholder="Password")
            submit = st.form_submit_button("Sign In")

            if submit:
                conn = get_conn()
                cur = conn.cursor(dictionary=True)
                cur.execute("SELECT * FROM users WHERE email=%s", (email,))
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


    # RIGHT SIDE
    with right:
        st.markdown("<div class='right-panel'>", unsafe_allow_html=True)

        st.markdown("<div class='brand'>Sales Buddy</div>", unsafe_allow_html=True)
        st.markdown("<div class='side-title'>New Here?</div>", unsafe_allow_html=True)
        st.markdown("<div class='side-text'>Sign up and discover a great amount of new opportunities!</div>", unsafe_allow_html=True)

        if st.button("Sign Up"):
            navigate("signup")

        st.markdown("</div>", unsafe_allow_html=True)


    st.markdown("</div>", unsafe_allow_html=True)
