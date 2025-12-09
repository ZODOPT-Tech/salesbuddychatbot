import streamlit as st
import mysql.connector
import bcrypt
import boto3
import json

# --- Configuration ---
# Set page to wide layout, essential for two-column design
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
    background:#ffffff;
    height:100%;
    display:flex;
    flex-direction:column;
    justify-content:center;
}

.title {
    font-size:56px;
    font-weight:800;
    margin-bottom:8px;
}

.subtitle {
    font-size:18px;
    color:#9aa1aa;
    margin-bottom:28px;
}

.card-wrapper {
    width:420px;
}

/* Styling for Email/Password Input Fields (Light Grey background) */
.stTextInput > div > div > input {
    background:#eef2f6 !important;
    border-radius:12px !important;
    border:none !important;
    padding:15px 14px !important;
    font-size:14px !important;
}

.stTextInput label {
    display:none !important;
}

/* --- Sign In Button (Green, inside form) --- */
.card-wrapper form button {
    background:#20c997 !important;
    color:#ffffff !important;
    border:none !important;
    border-radius:12px !important; 
    padding:12px 0 !important;
    font-weight:700 !important;
    font-size:17px !important;
    width:100% !important;
    margin-top:16px;
    height: auto !important;
}

/* --- Password Field Styling to match the Green Eye Icon --- */
.stTextInput:nth-child(2) > div > div {
    padding-right: 0px !important;
}

.stTextInput:nth-child(2) > div > div > input {
    border-top-right-radius: 0px !important;
    border-bottom-right-radius: 0px !important;
}
/* Targets the eye icon wrapper (the green button area) */
.stTextInput:nth-child(2) > div > div > button {
    background: #20c997 !important;
    color: #ffffff !important;
    border-radius: 12px !important;
    border-top-left-radius: 0px !important;
    border-bottom-left-radius: 0px !important;
    height: 100% !important;
    padding-left: 10px !important;
    padding-right: 10px !important;
    width: 60px !important;
}


/* --- RIGHT PANEL (Gradient Background) --- */
.right {
    height:100%;
    /* Gradient background from the image */
    background:linear-gradient(135deg, #00A6D9 0%, #008BD5 50%, #1CCABF 100%);
    display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:flex-start;
    padding: 70px 70px 70px 60px;
    position:relative;
    overflow: hidden;
}

/* Custom element to act as the decorative gradient banner */
.right-banner {
    position: absolute;
    top: 100px; 
    right: 100px;
    width: 200px;
    height: 60px;
    background: linear-gradient(90deg, #1ccdab, #00a6d9);
    border-radius: 5px;
    z-index: 2; 
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
.right-content {
    z-index: 5;
    color: #ffffff;
    /* Adjust vertical centering to match the image's higher placement */
    margin-top: -100px; 
}

.brand {
    font-size:28px;
    font-weight:700;
    margin-bottom:10px;
}

.nh {
    font-size:46px;
    font-weight:800;
    margin-bottom:10px;
}

.desc {
    font-size:18px;
    max-width:330px;
    margin-bottom:35px;
    color:#e8fbf8; 
    font-weight: 400;
}

/* --- Sign Up Button (Grey, on gradient background) --- */
.right-content .stButton button {
    background:#9aa1aa !important; /* Darker grey color */
    color:#ffffff !important;
    font-weight:700 !important;
    border-radius:8px !important; 
    padding:8px 30px !important;
    border:none !important;
    font-size:16px !important;
    width: auto !important;
    height: auto !important;
    margin-top: 10px;
}

</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# --- AWS Secrets and DB Connection Setup (Uses placeholder ARN) ---
SECRET_ARN = "arn:aws:secretsmanager:ap-south-1:034362058776:secret:salesbuddy/secrets-0xh2TS"

@st.cache_resource
def get_db():
    # NOTE: This function requires valid AWS credentials and a running RDS instance.
    # It will fail if the secret ARN is invalid or credentials are not configured.
    try:
        client = boto3.client("secretsmanager", region_name="ap-south-1")
        s = json.loads(client.get_secret_value(SecretId=SECRET_ARN)["SecretString"])
        return mysql.connector.connect(
            host=s["DB_HOST"],
            user=s["DB_USER"],
            password=s["DB_PASSWORD"],
            database=s["DB_NAME"],
        )
    except Exception as e:
        # Provide a friendly error message if the connection fails
        st.error(f"Database connection failed: Ensure AWS Secrets and Region are configured correctly.")
        st.stop()
        
# --- Streamlit Rendering Function ---
def render(navigate):
    st.markdown("<div class='page'>", unsafe_allow_html=True)
    col1, col2 = st.columns([2.7, 2], gap="small")

    # LEFT PANEL (Login)
    with col1:
        st.markdown("<div class='left'>", unsafe_allow_html=True)
        st.markdown(
            "<div class='title'>Login to Your<br>Account</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='subtitle'>Access your account</div>",
            unsafe_allow_html=True,
        )

        st.markdown("<div class='card-wrapper'>", unsafe_allow_html=True)
        with st.form("login"):
            email = st.text_input("", placeholder="Email")
            password = st.text_input("", placeholder="Password", type="password") 
            
            # The green "Sign In" button (form submit)
            ok = st.form_submit_button("Sign In")

            if ok:
                try:
                    conn = get_db()
                    cur = conn.cursor(dictionary=True)
                    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
                    user = cur.fetchone()
                    cur.close()
                    # conn.close() # Keep connection open if using @st.cache_resource
                    
                    if user and bcrypt.checkpw(
                        password.encode(), user["password"].encode()
                    ):
                        st.session_state.logged_in = True
                        st.session_state.user_data = user
                        navigate("chatbot")
                    else:
                        st.error("Incorrect email or password.")
                except Exception:
                    # Generic error for the login process itself
                    st.error("Login attempt failed. Please check your credentials.")

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # RIGHT PANEL (Gradient Background Sign Up)
    with col2:
        st.markdown("<div class='right'>", unsafe_allow_html=True)
        
        # Decorative gradient banner
        st.markdown("<div class='right-banner'></div>", unsafe_allow_html=True)

        # Content container
        st.markdown("<div class='right-content'>", unsafe_allow_html=True)
        
        # Brand Name
        st.markdown("<div class='brand'>Sales Buddy</div>", unsafe_allow_html=True)
        
        # New Here?
        st.markdown("<div class='nh'>New Here?</div>", unsafe_allow_html=True)
        
        # Description
        st.markdown(
            "<div class='desc'>Sign up and discover a great amount of new opportunities!</div>",
            unsafe_allow_html=True,
        )
        
        # Grey "Sign Up" button
        if st.button("Sign Up"):
            # In a real app, this would change the page state
            navigate("signup")
            
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# NOTE: In a multi-page Streamlit application, you would call this function 
# based on the navigation state. For a standalone file, you can call it directly 
# using a placeholder `Maps` function.

def placeholder_navigate(page_name):
    # This function simulates navigation in a multi-page app environment.
    st.info(f"Navigating to the **{page_name}** page (Simulated).")

if __name__ == "__main__":
    render(placeholder_navigate)
