import streamlit as st
import mysql.connector
import bcrypt
import boto3
import json

st.set_page_config(page_title="Sales Buddy | Login", layout="wide")

CSS = """
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');

* {
    font-family:'Poppins',sans-serif;
}

.stApp > header, .stApp > footer {
    display:none;
}

.stApp > main .block-container {
    padding:0 !important;
    margin:0 !important;
}

/* full page */
.page {
    width:100vw;
    height:100vh;
    overflow:hidden;
}

/* columns take full height */
[data-testid="stHorizontalBlock"] {
    height:100%;
}

/* LEFT PANEL */
.left {
    padding:60px 80px;
    background:white;
    height:100%;
    display:flex;
    flex-direction:column;
    justify-content:center;
}

.title {
    font-size:52px;
    font-weight:800;
    margin-bottom:10px;
}

.subtitle {
    font-size:19px;
    color:#7c8590;
    margin-bottom:35px;
}

/* form card */
.card {
    width:460px;
    background:white;
    border:1px solid #e1e3e7;
    padding:32px;
    border-radius:18px;
}

.stTextInput > div > div > input {
    background:#eef2f6 !important;
    border:none !important;
    border-radius:12px !important;
    padding:15px !important;
}

form button {
    background:linear-gradient(90deg,#1ad4af,#00a7d9) !important;
    color:white !important;
    border:none !important;
    border-radius:35px !important;
    padding:14px 0 !important;
    font-weight:700 !important;
    font-size:18px !important;
    width:100% !important;
    margin-top:20px;
}

/* RIGHT PANEL (FULL BG) */
.right {
    height:100%;
    padding:70px 60px;
    background:linear-gradient(140deg,#1ccdab,#00a6d9,#008bd5);
    display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:flex-start;
    color:white;
    position:relative;
}

/* decorative circles */
.right::before {
    content:"";
    position:absolute;
    width:320px;
    height:320px;
    top:80px;
    right:-90px;
    background:rgba(255,255,255,0.14);
    border-radius:50%;
}

.right::after {
    content:"";
    position:absolute;
    width:390px;
    height:390px;
    bottom:-120px;
    left:-110px;
    background:rgba(255,255,255,0.11);
    border-radius:50%;
}

/* Right text */
.brand {
    font-size:30px;
    font-weight:700;
    margin-bottom:60px;
    z-index:5;
}

.nh {
    font-size:46px;
    font-weight:800;
    margin-bottom:12px;
    z-index:5;
}

.desc {
    font-size:19px;
    max-width:330px;
    margin-bottom:35px;
    color:#e8fbf8;
    z-index:5;
}

/* Sign up button */
.right .stButton > button {
    background:white !important;
    color:#15b7a5 !important;
    font-weight:700 !important;
    border-radius:35px !important;
    padding:14px 40px !important;
    border:none !important;
    font-size:18px !important;
    z-index:10;
}

</style>
"""
st.markdown(CSS,unsafe_allow_html=True)


SECRET_ARN="arn:aws:secretsmanager:ap-south-1:034362058776:secret:salesbuddy/secrets-0xh2TS"

@st.cache_resource
def get_db():
    client=boto3.client("secretsmanager",region_name="ap-south-1")
    s=json.loads(client.get_secret_value(SecretId=SECRET_ARN)["SecretString"])
    return mysql.connector.connect(
        host=s["DB_HOST"],user=s["DB_USER"],
        password=s["DB_PASSWORD"],database=s["DB_NAME"]
    )

def render(navigate):

    st.markdown("<div class='page'>",unsafe_allow_html=True)

    # Adjusted width ratio
    col1,col2=st.columns([2.7,2],gap="small")

    # LEFT
    with col1:
        st.markdown("<div class='left'>",unsafe_allow_html=True)
        st.markdown("<div class='title'>Login to Your Account</div>",unsafe_allow_html=True)
        st.markdown("<div class='subtitle'>Access your account</div>",unsafe_allow_html=True)

        st.markdown("<div class='card'>",unsafe_allow_html=True)
        with st.form("login"):
            email=st.text_input("",placeholder="Email")
            password=st.text_input("",placeholder="Password",type="password")
            ok=st.form_submit_button("Sign In")
            if ok:
                conn=get_db()
                cur=conn.cursor(dictionary=True)
                cur.execute("SELECT * FROM users WHERE email=%s",(email,))
                user=cur.fetchone()
                cur.close()
                if user and bcrypt.checkpw(password.encode(),user["password"].encode()):
                    st.session_state.logged_in=True
                    st.session_state.user_data=user
                    navigate("chatbot")
                else:
                    st.error("Incorrect email or password.")
        st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)

    # RIGHT
    with col2:
        st.markdown("<div class='right'>",unsafe_allow_html=True)
        st.markdown("<div class='brand'>Sales Buddy</div>",unsafe_allow_html=True)
        st.markdown("<div class='nh'>New Here?</div>",unsafe_allow_html=True)
        st.markdown("<div class='desc'>Sign up and discover a great amount of new opportunities!</div>",unsafe_allow_html=True)
        if st.button("Sign Up"):
            navigate("signup")
        st.markdown("</div>",unsafe_allow_html=True)

    st.markdown("</div>",unsafe_allow_html=True)
