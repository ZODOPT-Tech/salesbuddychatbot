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
# GLOBAL CSS
# --------------------------------------------
CSS = """
<style>

* {
    font-family: "Inter", sans-serif;
}

.stApp > header {display:none;}
.stApp > footer {display:none;}

.stApp > main .block-container {
    padding: 0 !important;
    margin: 0 !important;
}

.page-wrapper {
    height: 100vh;
    width: 100vw;
    overflow: hidden;
}

/* Make columns fill full height */
[data-testid="stHorizontalBlock"] {
    height: 100%;
}

/* LEFT PANEL */
.left-panel {
    height:100%;
    background:#ffffff;
    padding:70px 90px;
    display:flex;
    flex-direction:column;
    justify-content:center;
}

.logo-text {
    font-size:28px;
    font-weight:700;
    color:#1b1d25;
    margin-bottom:45px;
}

.main-heading {
    font-size:44px;
    font-weight:800;
    margin-bottom:10px;
    color:#151821;
}

.subtext {
    font-size:18px;
    color:#77808a;
    margin-bottom:40px;
}

/* Input box */
.stTextInput > div > div > input {
    background:#eef3f6 !important;
    border:none !important;
    border-radius:14px !important;
    padding:16px !important;
    font-size:17px !important;
}

.stTextInput input::placeholder {
    color:#9ca3af;
}

/* Submit button inside form */
.left-panel form button {
    background:linear-gradient(90deg,#27c4a8,#23a6d5) !important;
    border:none !important;
    border-radius:40px !important;
    padding:15px 0 !important;
    width:100% !important;
    font-size:18px !important;
    font-weight:700 !important;
    color:#ffffff !important;
    margin-top:25px !important;
}

/* RIGHT PANEL */
.right-panel {
    height:100%;
    color:white;
    padding:80px 60px;
    background:linear-gradient(180deg,#27c4a8,#23a6d5);
    position:relative;
    display:flex;
    flex-direction:column;
    justify-content:center;
}

/* Abstract circles */
.right-panel::before {
    content:"";
    position:absolute;
    width:200px;
    height:200px;
    background:rgba(255,255,255,0.16);
    border-radius:50%;
    top:12%;
    right:-50px;
}

.right-panel::after {
    content:"";
    position:absolute;
    width:280px;
    height:280px;
    background:rgba(255,255,255,0.14);
    border-radius:50%;
    bottom:-60px;
    left:-60px;
}

.side-title {
    font-size:40px;
    font-weight:800;
    margin-bottom:16px;
    position:relative;
    z-index:10;
}

.side-text {
    font-size:18px;
    line-height:1.4;
    color:#e4fbf7;
    margin-bottom:40px;
    position:relative;
    z-index:10;
}

.right-panel .stButton > button {
    background:#ffffff !important;
    color:#20b5a3 !important;
    border-radius:40px !important;
    padding:14px 45px !important;
    font-size:18px !important;
    font-weight:700 !important;
    border:none !important;
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
# RENDER LOGIN UI
# --------------------------------------------
def render(navigate):

    st.markdown("<div class='page-wrapper'>", unsafe_allow_html=True)

    col_left, col_right = st.columns([3,2], gap="small")

    # ---------------- LEFT PANEL ----------------
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
                        cur.execute("""
                            SELECT user_id, full_name, email, company, password
                            FROM users WHERE email=%s
                        """, (email,))
                        user = cur.fetchone()
                        cur.close()

                        if user and bcrypt.checkpw(
                            password.encode('utf-8'),
                            user['password'].encode('utf-8')
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


    # ---------------- RIGHT PANEL ----------------
    with col_right:
        st.markdown("<div class='right-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='side-title'>New Here?</div>", unsafe_allow_html=True)
        st.markdown("<div class='side-text'>Sign up and discover a great amount of new opportunities!</div>", unsafe_allow_html=True)

        if st.button("Sign Up"):
            navigate("signup")

        st.markdown("</div>", unsafe_allow_html=True)


    st.markdown("</div>", unsafe_allow_html=True)
