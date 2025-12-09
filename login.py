import streamlit as st
import mysql.connector
import bcrypt
import base64
import requests

# ---------------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------------
st.set_page_config(
    page_title="Sales Buddy | Login",
    layout="wide",
)

# ---------------------------------------------------------------
# BACKGROUND IMAGE SET
# ---------------------------------------------------------------
def set_background(url):
    img = requests.get(url).content
    encoded = base64.b64encode(img).decode()
    st.markdown(
        f"""
        <style>
        /* FULL BACKGROUND */
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background("https://images.unsplash.com/photo-1542281286-9e0a16bb7366")


# ---------------------------------------------------------------
# CRITICAL FIXES (NO GAP + NO SCROLL)
# ---------------------------------------------------------------
st.markdown("""
<style>

/* Remove top gap */
.stApp {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

/* Remove block-container padding */
.block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
}

/* Remove default header/footer */
.stApp > header, .stApp > footer {
    display: none !important;
}

/* Remove scrollbar */
html, body {
    height: 100%;
    overflow: hidden !important;
}

/* Wrapper takes full height */
.fullscreen {
    height: 100vh;
    width: 100vw;
    display: flex;
    flex-direction: row;
    padding: 0;
    margin: 0;
}

/* Left side */
.left {
    flex: 1;
    padding: 80px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

/* Right side */
.right {
    flex: 1;
    padding: 80px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    background: rgba(0,0,0,0.35);
    backdrop-filter: blur(8px);
}

/* Title */
.title {
    font-size: 60px;
    font-weight: 800;
    line-height: 1.1;
    color: white;
}

/* Subtitle */
.sub {
    font-size: 20px;
    margin-top:10px;
    margin-bottom: 40px;
    color: white;
}

/* Glass form box */
.form-box {
    background: rgba(0,0,0,0.60);
    backdrop-filter: blur(10px);
    padding: 40px;
    border-radius: 22px;
    width: 500px;
}

/* Inputs */
.stTextInput > div > div > input {
    background:#121212 !important;
    color:white !important;
    border: 1px solid #666 !important;
    border-radius:12px !important;
    padding: 14px !important;
    font-size:18px;
}

/* Button */
form button, .stButton>button {
    background:#00b894 !important;
    color:white !important;
    font-weight:700 !important;
    border:none !important;
    padding:16px !important;
    border-radius:14px !important;
    font-size:20px !important;
    width:100% !important;
    margin-top: 14px;
}

.right-title {
    font-size:60px;
    font-weight:800;
    line-height:1.1;
    margin-bottom:32px;
    color:white;
}

.right-text {
    max-width:360px;
    font-size:21px;
    color:white;
    margin-bottom:50px;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------
# DB CONNECTION
# ---------------------------------------------------------------
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="salesbuddy"
    )


# ---------------------------------------------------------------
# UI
# ---------------------------------------------------------------
def render(navigate):

    st.markdown("<div class='fullscreen'>", unsafe_allow_html=True)

    col1, col2 = st.columns([1,1])

    # ---------------- LEFT ----------------
    with col1:
        st.markdown("<div class='left'>", unsafe_allow_html=True)

        st.markdown("<div class='title'>Login to Your<br>Account</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub'>Access your account</div>", unsafe_allow_html=True)

        st.markdown("<div class='form-box'>", unsafe_allow_html=True)
        with st.form("login"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            ok = st.form_submit_button("Sign In")

            if ok:
                try:
                    conn = get_db()
                    cur = conn.cursor(dictionary=True)
                    cur.execute("SELECT * FROM users WHERE email=%s",(email,))
                    user = cur.fetchone()
                    cur.close()

                    if user and bcrypt.checkpw(password.encode(),user["password"].encode()):
                        st.session_state.logged_in=True
                        st.session_state.user_data=user
                        navigate("dashboard")
                    else:
                        st.error("Incorrect details")
                except Exception as e:
                    st.error("Login failed")

        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- RIGHT ----------------
    with col2:
        st.markdown("<div class='right'>", unsafe_allow_html=True)
        st.markdown("<div class='right-title'>New Here?</div>", unsafe_allow_html=True)
        st.markdown("<div class='right-text'>Sign up and discover a great amount of new opportunities!</div>", unsafe_allow_html=True)

        if st.button("Sign Up"):
            navigate("signup")

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------
# LOCAL TEST
# ---------------------------------------------------------------
if __name__ == "__main__":
    def go(x):
        st.success(f"Nav → {x}")
    render(go)
