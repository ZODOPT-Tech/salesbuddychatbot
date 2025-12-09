import streamlit as st
import mysql.connector
import bcrypt
import boto3
import json

st.set_page_config(page_title="Sales Buddy | Login", layout="wide")

# ---------------------------------------------------
# CSS
# ---------------------------------------------------
CSS = """
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');

* {
    font-family: 'Poppins', sans-serif;
}

.stApp > header, .stApp > footer {display:none;}

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

/* LEFT PANEL */
.left {
    background: #ffffff;
    height:100%;
    padding: 60px 90px;
    display:flex;
    flex-direction:column;
    justify-content:center;
}

.title {
    font-size:52px;
    font-weight:800;
    color:#14161c;
    line-height:1.1;
    margin-bottom:15px;
}

.subtitle {
    font-size:19px;
    color:#7b8592;
    margin-bottom:45px;
}

/* Form card box */
.form-box {
    background:#ffffff;
    border:1px solid #e1e3e7;
    border-radius:20px;
    padding:35px 28px;
    width:460px;
}

/* Inputs */
.stTextInput > div > div > input {
    background:#eef2f6 !important;
    border:none !important;
    border-radius:14px !important;
    padding:16px !important;
    font-size:17px !important;
}

.stTextInput input::placeholder {
    color:#9ca3af;
}

/* Login button */
form button {
    background:linear-gradient(90deg,#1ccdab,#00a6d9) !important;
    color:#fff !important;
    font-weight:700 !important;
    border-radius:40px !important;
    padding:14px 0 !important;
    border:none !important;
    font-size:18px !important;
    width:100% !important;
    margin-top:22px;
}

/* RIGHT PANEL FULL BACKGROUND */
.right {
    height:100%;
    padding: 80px 85px;
    background: linear-gradient(140deg,#1ccdab,#00a6d9,#008bd5);
    display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:flex-start;
    color:white;
    position:relative;
}

/* Abstract shapes */
.right::before {
    content:"";
    position:absolute;
    width:300px;
    height:300px;
    top:60px;
    right:-80px;
    background:rgba(255,255,255,0.14);
    border-radius:50%;
    filter:blur(1px);
}

.right::after {
    content:"";
    position:absolute;
    width:380px;
    height:380px;
    bottom:-100px;
    left:-100px;
    background:rgba(255,255,255,0.12);
    border-radius:50%;
    filter:blur(1px);
}

/* Branding */
.brand {
    font-size:30px;
    font-weight:700;
    margin-bottom:70px;
    z-index:5;
}

/* New Here text */
.nh-title {
    font-size:46px;
    font-weight:800;
    margin-bottom:18px;
    z-index:5;
}

.nh-text {
    font-size:19px;
    opacity:0.92;
    max-width:360px;
    line-height:1.45;
    margin-bottom:40px;
    z-index:5;
}

.right .stButton > button {
    background:white !important;
    color:#14b7a4 !important;
    font-weight:700 !important;
    padding:14px 45px !important;
    border-radius:40px !important;
    border:none !important;
    font-size:18px !important;
    z-index:10;
}

</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------------------------------------------------
# AWS Secrets
# ---------------------------------------------------
SECRET_ARN="arn:aws:secretsmanager:ap-south-1:034362058776:secret:salesbuddy/secrets-0xh2TS"

@st.cache_resource
def get_db_secrets():
    client=boto3.client("secretsmanager",region_name="ap-south-1")
    return json.loads(client.get_secret_value(SecretId=SECRET_ARN)["SecretString"])

@st.cache_resource
def get_conn():
    s=get_db_secrets()
    return mysql.connector.connect(
        host=s["DB_HOST"],user=s["DB_USER"],
        password=s["DB_PASSWORD"],database=s["DB_NAME"]
    )

# ---------------------------------------------------
# RENDER
# ---------------------------------------------------
def render(navigate):

    st.markdown("<div class='page-wrapper'>",unsafe_allow_html=True)

    col1,col2=st.columns([3,2],gap="small")

    # LEFT
    with col1:
        st.markdown("<div class='left'>",unsafe_allow_html=True)
        st.markdown("<div class='title'>Login to Your Account</div>",unsafe_allow_html=True)
        st.markdown("<div class='subtitle'>Access your account</div>",unsafe_allow_html=True)

        st.markdown("<div class='form-box'>",unsafe_allow_html=True)
        with st.form("login"):
            email=st.text_input("",placeholder="Email")
            password=st.text_input("",type="password",placeholder="Password")
            login=st.form_submit_button("Sign In")
            if login:
                conn=get_conn()
                cur=conn.cursor(dictionary=True)
                cur.execute("SELECT * FROM users WHERE email=%s",(email,))
                u=cur.fetchone()
                cur.close()
                if u and bcrypt.checkpw(password.encode(),u["password"].encode()):
                    st.session_state.logged_in=True
                    st.session_state.user_data=u
                    navigate("chatbot")
                else:
                    st.error("Wrong email or password.")
        st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)

    # RIGHT
    with col2:
        st.markdown("<div class='right'>",unsafe_allow_html=True)
        st.markdown("<div class='brand'>Sales Buddy</div>",unsafe_allow_html=True)
        st.markdown("<div class='nh-title'>New Here?</div>",unsafe_allow_html=True)
        st.markdown("<div class='nh-text'>Sign up and discover a great amount of new opportunities!</div>",unsafe_allow_html=True)
        if st.button("Sign Up"):
            navigate("signup")
        st.markdown("</div>",unsafe_allow_html=True)

    st.markdown("</div>",unsafe_allow_html=True)
