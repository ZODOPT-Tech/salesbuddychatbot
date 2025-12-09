import streamlit as st
import mysql.connector
import bcrypt
import boto3
import json


# -------------------------------------------------------
# CSS for Full UI
# -------------------------------------------------------
CSS = """
<style>

body, html {
    margin: 0;
    padding: 0;
}

.stApp {
    background: #ffffff;
    font-family: "Inter", sans-serif;
}

/* MAIN WRAPPER */
.login-wrapper {
    display: flex;
    width: 100%;
    height: 100vh;
}

/* LEFT PANEL */
.left-panel {
    width: 60%;
    padding: 80px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.logo {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 60px;
}

.logo-text {
    font-size: 26px;
    font-weight: 700;
    color: #34495e;
}

/* Title */
.login-title {
    font-size: 46px;
    font-weight: 800;
    color: #212b36;
    margin-bottom: 8px;
}

.login-sub {
    font-size: 18px;
    color: #7f8c8d;
    margin-bottom: 35px;
}

/* Divider */
.divider {
    display: flex;
    align-items: center;
    margin: 30px 0px;
}

.divider-line {
    flex: 1;
    height: 1px;
    background: #e0e0e0;
}

.divider-text {
    margin: 0 15px;
    color: #9a9ea2;
    font-size: 14px;
}

/*** INPUTS ***/
.stTextInput > div > div > input {
    background: #eef3f5 !important;
    border-radius: 12px !important;
    border: none !important;
    padding: 14px !important;
    font-size: 16px !important;
}

.stTextInput > div > div > input::placeholder {
    color: #879199;
}

/*** LOGIN BUTTON ***/
.login-btn button {
    width: 100%;
    background: linear-gradient(90deg,#32c19f,#00a0b8) !important;
    border: none !important;
    padding: 14px 0 !important;
    border-radius: 30px !important;
    color: #fff !important;
    font-size: 18px !important;
    font-weight: 600 !important;
    margin-top: 10px;
}


/* RIGHT PANEL (SIGNUP) */
.right-panel {
    width: 40%;
    background: linear-gradient(180deg, #27c2a4, #2ea6d6);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    color: white;
    position: relative;
    padding: 40px;
    text-align: center;
}

/* Abstract Shapes */
.right-panel::before {
    content: "";
    position: absolute;
    top: 10%;
    right: 20%;
    width: 140px;
    height: 140px;
    background: rgba(255,255,255,0.08);
    border-radius: 50%;
}

.right-panel::after {
    content: "";
    position: absolute;
    bottom: 12%;
    right: 10%;
    width: 200px;
    height: 200px;
    background: rgba(255,255,255,0.08);
    border-radius: 50%;
}


.signup-title {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 14px;
}

.signup-text {
    font-size: 18px;
    color: #def7f3;
    margin-bottom: 35px;
}

/*** SIGN UP BUTTON ***/
.signup-btn button {
    background: white !important;
    color: #20b8a2 !important;
    padding: 14px 40px !important;
    border-radius: 50px !important;
    font-size: 18px !important;
    font-weight: 600 !important;
    border: none !important;
}

.signup-btn button:hover {
    opacity: 0.9;
}

</style>
"""
st.markdown(CSS, unsafe_allow_html=True)



# -------------------------------------------------------
# AWS SECRET (KEEP YOUR ORIGINAL)
# -------------------------------------------------------
SECRET_ARN = "arn:aws:secretsmanager:ap-south-1:034362058776:secret:salesbuddy/secrets-0xh2TS"


@st.cache_resource
def get_db_secrets():
    client = boto3.client("secretsmanager", region_name="ap-south-1")
    resp = client.get_secret_value(SecretId=SECRET_ARN)
    raw = json.loads(resp["SecretString"])
    return raw


@st.cache_resource
def get_conn():
    creds = get_db_secrets()
    conn = mysql.connector.connect(
        host=creds["DB_HOST"],
        user=creds["DB_USER"],
        password=creds["DB_PASSWORD"],
        database=creds["DB_NAME"],
        charset="utf8mb4"
    )
    return conn


# -------------------------------------------------------
# LOGIN RENDER UI
# -------------------------------------------------------
def render(navigate):
    
    st.markdown("<div class='login-wrapper'>", unsafe_allow_html=True)

    # ---------------- LEFT PANEL ----------------
    st.markdown("<div class='left-panel'>", unsafe_allow_html=True)

    # Logo
    st.markdown("""
        <div class='logo'>
            <img src="https://cdn-icons-png.flaticon.com/512/149/149071.png" width="48">
            <div class='logo-text'>Sales Buddy</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='login-title'>Login to Your Account</div>", unsafe_allow_html=True)
    st.markdown("<div class='login-sub'>Access your account</div>", unsafe_allow_html=True)

    with st.form("login_form"):
        email = st.text_input("Email", placeholder="Email")
        password = st.text_input("Password", type="password", placeholder="Password")
        submitted = st.form_submit_button("Sign In")

        if submitted:
            conn = get_conn()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT user_id, full_name, email, company, password FROM users WHERE email=%s", (email,))
            user = cur.fetchone()
            cur.close()

            if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                st.session_state.logged_in = True
                st.session_state.user_data = {
                    "user_id": user["user_id"],
                    "full_name": user["full_name"],
                    "email": user["email"],
                    "company": user["company"]
                }
                navigate("chatbot")
            else:
                st.error("Incorrect email or password")

    st.markdown("</div>", unsafe_allow_html=True)


    # ---------------- RIGHT PANEL ----------------
    st.markdown("<div class='right-panel'>", unsafe_allow_html=True)

    st.markdown("<div class='signup-title'>New Here?</div>", unsafe_allow_html=True)
    st.markdown("""
        <div class='signup-text'>
            Sign up and discover a great amount of new opportunities!
        </div>
    """, unsafe_allow_html=True)

    if st.button("Sign Up", key="signup", help=None, type="primary"):
        navigate("signup")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
