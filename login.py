import streamlit as st
import mysql.connector
import bcrypt
import boto3
import json


# -------------------------------------------------------
# CSS
# -------------------------------------------------------
CSS = """
<style>

* {
    font-family: "Inter", sans-serif;
}

.stApp {
    background: #ffffff;
    padding: 0 !important;
}

.container-full {
    display: flex;
    flex-direction: row;
    height: 100vh;
    width: 100vw;
    overflow: hidden;
}

/* LEFT PANEL */
.left {
    width: 55%;
    padding: 80px 120px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.logo-title {
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 45px;
    color: #1d1e20;
}

.main-heading {
    font-size: 44px;
    font-weight: 900;
    color: #1c1d21;
    margin-bottom: 10px;
}

.subtext {
    font-size: 18px;
    color: #9199a4;
    margin-bottom: 35px;
}

/* Inputs look */
.stTextInput > div > div > input {
    background: #eef2f4 !important;
    border-radius: 14px !important;
    border: none !important;
    padding: 16px !important;
    font-size: 18px !important;
}

.stTextInput input::placeholder {
    color: #9ca3af;
}

/* Sign In Button */
.sign-btn button {
    background: linear-gradient(90deg,#26c0a2,#2ca7cd) !important;
    border-radius: 40px !important;
    padding: 16px 0 !important;
    border: none !important;
    color: #fff !important;
    font-size: 19px !important;
    font-weight: 700 !important;
    width: 100% !important;
    margin-top: 25px;
}

/* RIGHT PANEL */
.right {
    width: 45%;
    background: linear-gradient(180deg, #26c0a2 0%, #2ca7cd 100%);
    color: #fff;
    position: relative;
    padding: 120px 80px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

/* Abstract circles */
.right::before {
    content: "";
    position: absolute;
    width: 240px;
    height: 240px;
    background: rgba(255,255,255,0.13);
    border-radius: 50%;
    top: 12%;
    right: -40px;
}

.right::after {
    content: "";
    position: absolute;
    width: 300px;
    height: 300px;
    background: rgba(255,255,255,0.12);
    border-radius: 50%;
    bottom: -40px;
    left: -30px;
}

.side-title {
    font-size: 46px;
    font-weight: 900;
    margin-bottom: 15px;
}

.side-text {
    font-size: 20px;
    color: #e4fbf7;
    margin-bottom: 45px;
    line-height: 1.4;
}

/* Sign Up Btn */
.signup-btn button {
    background: #fff !important;
    border-radius: 40px !important;
    color: #25b9a3 !important;
    font-size: 19px !important;
    font-weight: 700 !important;
    padding: 16px 50px !important;
    border: none !important;
}

</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# -------------------------------------------------------
# Secrets
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
# UI
# -------------------------------------------------------
def render(navigate):
 
    st.markdown("<div class='container-full'>", unsafe_allow_html=True)

    # LEFT SIDE
    st.markdown("<div class='left'>", unsafe_allow_html=True)
    st.markdown("<div class='logo-title'>Sales Buddy</div>", unsafe_allow_html=True)
    st.markdown("<div class='main-heading'>Login to Your Account</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtext'>Access your account</div>", unsafe_allow_html=True)

    with st.form("loginform"):
        email = st.text_input("", placeholder="Email")
        password = st.text_input("", type="password", placeholder="Password")
        login_btn = st.form_submit_button("Sign In")

        if login_btn:
            conn = get_conn()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT user_id, full_name, email, company, password FROM users WHERE email=%s", (email,))
            user = cur.fetchone()
            cur.close()

            if user and bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
                st.session_state.logged_in = True
                st.session_state.user_data = user
                navigate("chatbot")
            else:
                st.error("Incorrect email or password")
    st.markdown("</div>", unsafe_allow_html=True)


    # RIGHT SIDE
    st.markdown("<div class='right'>", unsafe_allow_html=True)
    st.markdown("<div class='side-title'>New Here?</div>", unsafe_allow_html=True)
    st.markdown("<div class='side-text'>Sign up and discover a great amount of new opportunities!</div>", unsafe_allow_html=True)

    if st.button("Sign Up"):
        navigate("signup")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
