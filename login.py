import streamlit as st
import mysql.connector
import bcrypt
import boto3
import json

# ---- PAGE SETUP ----
st.set_page_config(page_title="Sales Buddy | Login", layout="wide")


# ---- CSS ----
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');

* {
    font-family: 'Poppins', sans-serif;
}

.stApp > header, .stApp > footer {display:none !important;}

.stApp > main .block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
}

.wrapper {
    display: flex;
    height: 100vh;
    overflow: hidden;
}

/* Left Panel */
.left {
    flex: 1;
    padding: 80px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    background: #ffffff;
}

.title {
    font-size: 48px;
    font-weight:800;
    margin-bottom: 10px;
}

.subtitle {
    font-size:18px;
    color:#7c8590;
    margin-bottom:40px;
}

.input-block input {
    background: #eef2f6 !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px !important;
}

form button {
    background:#00b894 !important;
    color:white !important;
    border:none !important;
    border-radius: 12px !important;
    padding:14px !important;
    font-size: 18px !important;
    font-weight:700 !important;
    width:100%;
    margin-top: 25px;
}

/* Right Panel */
.right {
    flex: 1;
    padding: 80px;
    color: white;
    display: flex;
    flex-direction: column;
    justify-content: center;
    background-size: cover !important;
    background-position: center !important;
    background-repeat: no-repeat !important;
    position: relative;
}

.overlay {
    position:absolute;
    top:0; left:0;
    width:100%; height:100%;
    background: rgba(0,0,0,0.36);
    border-radius: 0;
}

.brand {
    font-size:32px;
    font-weight:700;
    margin-bottom:30px;
    z-index: 10;
}

.nh {
    font-size:46px;
    font-weight:800;
    margin-bottom:10px;
    z-index: 10;
}

.desc {
    font-size:19px;
    max-width:330px;
    margin-bottom:40px;
    z-index: 10;
    color:#e9ffff;
}

.right .stButton>button {
    background:white !important;
    color:#00a896 !important;
    font-weight:700 !important;
    border-radius: 40px !important;
    padding:14px 40px !important;
    font-size:18px !important;
    border:none !important;
    z-index: 10;
}
</style>
""", unsafe_allow_html=True)


# ---- DB ----
SECRET_ARN = "arn:aws:secretsmanager:ap-south-1:034362058776:secret:salesbuddy/secrets-0xh2TS"

@st.cache_resource
def get_db():
    client = boto3.client("secretsmanager", region_name="ap-south-1")
    s = json.loads(client.get_secret_value(SecretId=SECRET_ARN)["SecretString"])
    return mysql.connector.connect(
        host=s["DB_HOST"], user=s["DB_USER"],
        password=s["DB_PASSWORD"], database=s["DB_NAME"]
    )


# ---- RENDER ----
def render(navigate):

    st.markdown(
        f"<div class='wrapper'>",
        unsafe_allow_html=True
    )

    # LEFT PANEL
    left, right = st.columns([1,1])
    with left:
        st.markdown("<div class='left'>", unsafe_allow_html=True)
        st.markdown("<div class='title'>Login to Your<br>Account</div>", unsafe_allow_html=True)
        st.markdown("<div class='subtitle'>Access your account</div>", unsafe_allow_html=True)

        with st.form("login"):
            email = st.text_input("", placeholder="Email", key="email")
            password = st.text_input("", placeholder="Password", type="password", key="pass")
            submit = st.form_submit_button("Sign In")

            if submit:
                conn = get_db()
                cur = conn.cursor(dictionary=True)
                cur.execute("SELECT * FROM users WHERE email=%s", (email,))
                user = cur.fetchone()
                cur.close()
                if user and bcrypt.checkpw(password.encode(), user["password"].encode()):
                    st.session_state.logged_in = True
                    st.session_state.user_data = user
                    navigate("chatbot")
                else:
                    st.error("Incorrect email or password")

        st.markdown("</div>", unsafe_allow_html=True)

    # RIGHT PANEL
    with right:
        # IMPORTANT → SET IMAGE HERE
        img_url = "https://i.postimg.cc/...png"   # Replace with your uploaded image
        st.markdown(
            f"<div class='right' style=\"background-image:url('{img_url}');\">",
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='overlay'></div>", unsafe_allow_html=True)
        
        st.markdown("<div class='brand'>Sales Buddy</div>", unsafe_allow_html=True)
        st.markdown("<div class='nh'>New Here?</div>", unsafe_allow_html=True)
        st.markdown("<div class='desc'>Sign up and discover great opportunities!</div>", unsafe_allow_html=True)
        
        if st.button("Sign Up"):
            navigate("signup")
        
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# LOCAL TEST
if __name__ == "__main__":
    def navigate(page): st.info(f"Navigate: {page}")
    render(navigate)
