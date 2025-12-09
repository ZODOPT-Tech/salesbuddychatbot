import streamlit as st
import mysql.connector
import bcrypt
import boto3
import json

# Set page to wide layout and title
st.set_page_config(page_title="Sales Buddy | Login", layout="wide")

# --- CSS Styling for the Perfect Layout ---
CSS = """
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');

* {
    font-family:'Poppins',sans-serif;
    box-sizing:border-box;
}

/* Hide Streamlit default header/footer */
.stApp > header, .stApp > footer {
    display:none;
}

/* 1. Full-Screen, No-Scroll Setup */
.stApp > main .block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
    min-height: 100vh;
}

.page {
    width: 100vw;
    height: 100vh;
    overflow: hidden; /* Prevent scrolling */
    display: flex;
}

[data-testid="stHorizontalBlock"] {
    height: 100%;
    width: 100%;
}

/* --- LEFT PANEL (Login Form) --- */
.left {
    padding:60px 90px;
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

.card {
    width:460px;
    background:white;
    padding:0; 
    border-radius:0;
    border: none;
}

/* Styling for Email/Password Input Fields (Light Grey background) */
.stTextInput > div > div > input {
    background:#eef2f6 !important;
    border:none !important;
    border-radius:12px !important;
    padding:15px !important;
}

.stTextInput label {
    display: none;
}

/* --- Sign In Button (Green, square corners, inside form) --- */
form button {
    background:#20c997 !important; 
    color:white !important;
    border:none !important;
    border-radius:12px !important; 
    padding:12px 0 !important;
    font-weight:700 !important;
    font-size:18px !important;
    width:100% !important;
    margin-top:20px;
}

/* --- Password Field Styling to match the Green Eye Icon/Area --- */

/* 1. Make the password input element itself have a non-rounded right side */
.stTextInput:nth-child(2) > div > div > input {
    border-top-right-radius: 0px !important;
    border-bottom-right-radius: 0px !important;
    padding-right: 15px !important;
}

/* 2. Target the button element next to the password input (the eye icon) */
.stTextInput:nth-child(2) > div > div > button {
    background: #20c997 !important; /* Green background */
    color: #ffffff !important;
    border-radius: 12px !important;
    border-top-left-radius: 0px !important;
    border-bottom-left-radius: 0px !important;
    height: 100% !important;
    padding-left: 10px !important;
    padding-right: 10px !important;
    width: 60px !important;
}

/* --- RIGHT PANEL (FULL BG) --- */
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
    overflow: hidden;
}

/* Decorative Circles */
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

/* Content wrapper to position the text */
.right-content-wrapper {
    margin-top: -100px; /* Shift content up slightly for better balance */
    z-index: 5;
}

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
    try:
        client=boto3.client("secretsmanager",region_name="ap-south-1")
        s=json.loads(client.get_secret_value(SecretId=SECRET_ARN)["SecretString"])
        return mysql.connector.connect(
            host=s["DB_HOST"],user=s["DB_USER"],
            password=s["DB_PASSWORD"],database=s["DB_NAME"]
        )
    except Exception as e:
        st.error(f"DB connection error: {e}")
        # Return None or raise an exception to stop further execution if critical
        st.stop()
        
def render(navigate):

    st.markdown("<div class='page'>",unsafe_allow_html=True)

    col1,col2=st.columns([2.7,2],gap="small")

    # LEFT PANEL (Login)
    with col1:
        st.markdown("<div class='left'>",unsafe_allow_html=True)
        st.markdown("<div class='title'>Login to Your<br>Account</div>",unsafe_allow_html=True)
        st.markdown("<div class='subtitle'>Access your account</div>",unsafe_allow_html=True)

        st.markdown("<div class='card'>",unsafe_allow_html=True)
        with st.form("login"):
            email=st.text_input("",placeholder="Email")
            password=st.text_input("",placeholder="Password",type="password") 
            
            # The Sign In button
            ok=st.form_submit_button("Sign In")
            
            if ok:
                try:
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
                except Exception as e:
                    # Generic error for the login process itself (excluding DB connection issues handled above)
                    st.error(f"Login failed: {e}")

        st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)

    # RIGHT PANEL (Sign Up)
    with col2:
        st.markdown("<div class='right'>",unsafe_allow_html=True)
        
        # Wrapper for content to allow vertical repositioning via CSS
        st.markdown("<div class='right-content-wrapper'>", unsafe_allow_html=True)
        
        st.markdown("<div class='brand'>Sales Buddy</div>",unsafe_allow_html=True)
        st.markdown("<div class='nh'>New Here?</div>",unsafe_allow_html=True)
        st.markdown("<div class='desc'>Sign up and discover a great amount of new opportunities!</div>",unsafe_allow_html=True)
        
        if st.button("Sign Up"):
            navigate("signup")

        st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)

    st.markdown("</div>",unsafe_allow_html=True)


if __name__ == "__main__":
    # Define a simple placeholder function for the 'navigate' argument
    def placeholder_navigate(page_name):
        # Initialize session state if running in a single file
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
            
        st.info(f"Navigation triggered to: **{page_name}**")
        
    # Run the render function
    render(placeholder_navigate)
