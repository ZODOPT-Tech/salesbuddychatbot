import streamlit as st
import mysql.connector
import bcrypt
import boto3
import json

# --- Configuration ---
st.set_page_config(page_title="Sales Buddy | Login", layout="wide")

# --- CSS Styling for Professional Look (Based on New Image) ---
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');

* {
    font-family:'Poppins',sans-serif;
    box-sizing:border-box;
}

.stApp > header, .stApp > footer {
    display:none;
}

/* Ensure the main container takes full viewport height and remove default padding/margin */
.stApp > main .block-container {
    padding:0 !important;
    margin:0 !important;
    max-width: 100% !important;
    min-height: 100vh;
}

/* full page wrapper */
.page {
    width:100vw;
    height:100vh;
    overflow:hidden;
    display: flex;
}

/* make columns full height */
[data-testid="stHorizontalBlock"] {
    height:100%;
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

/* form card wrapper - simplified */
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

/* Styling for the GREEN Sign In button (inside the form) */
/* Targeting the form submit button */
.card-wrapper form button {
    background:#20c997 !important;
    color:#ffffff !important;
    border:none !important;
    border-radius:12px !important; /* Made border radius smaller to match inputs */
    padding:12px 0 !important;
    font-weight:700 !important;
    font-size:17px !important;
    width:100% !important;
    margin-top:16px;
    height: auto !important; /* Ensure the button height is correct */
}

/* Ensure the password input area's color matches the password visibility button */
/* This is a common Streamlit hack to style the password input block */
.stTextInput:nth-child(2) > div > div {
    padding-right: 0px !important; /* Remove padding */
}

/* Additional styling to make the password field look like the image (green section) */
.stTextInput:nth-child(2) > div > div > input {
    border-top-right-radius: 0px !important;
    border-bottom-right-radius: 0px !important;
}
/* This targets the eye icon wrapper (the green button area) */
.stTextInput:nth-child(2) > div > div > button {
    background: #20c997 !important;
    color: #ffffff !important;
    border-radius: 12px !important;
    border-top-left-radius: 0px !important;
    border-bottom-left-radius: 0px !important;
    height: 100% !important;
    padding-left: 10px !important;
    padding-right: 10px !important;
    width: 60px !important; /* Adjust width to match the image */
}

/* --- RIGHT PANEL (Sign Up) --- */
.right {
    height:100%;
    background:#ffffff; /* WHITE Background */
    display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:flex-start;
    padding: 70px 90px;
    position:relative;
}

/* Custom element to act as the decorative gradient banner on the right side */
.right-banner {
    position: absolute;
    top: 150px; 
    right: 200px; /* Position it high up and slightly right */
    width: 200px;
    height: 60px;
    /* Gradient matching the one in the image */
    background: linear-gradient(90deg, #1ccdab, #00a6d9);
    border-radius: 5px;
    z-index: 2; 
}

/* Content wrapper to center the text and button */
.right-content {
    z-index: 5;
    margin-top: -150px; /* Adjust vertical centering */
}

.brand {
    font-size:24px;
    font-weight:700;
    color: #1c2a38;
    margin-bottom:10px;
}

.nh {
    font-size:46px;
    font-weight:800;
    margin-bottom:10px;
    color: #1c2a38;
}

.desc {
    font-size:18px;
    max-width:380px;
    margin-bottom:35px;
    color:#b3bfcc; /* Light cyan/grey for the description */
    font-weight: 600;
}

/* Styling for the GREY Sign Up button (outside the form) */
.right-content .stButton button {
    background:#9aa1aa !important; /* Darker grey color */
    color:#ffffff !important;
    font-weight:700 !important;
    border-radius:8px !important; /* Smaller radius */
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

# --- AWS Secrets and DB Connection Setup (Kept as is) ---
SECRET_ARN = "arn:aws:secretsmanager:ap-south-1:034362058776:secret:salesbuddy/secrets-0xh2TS"

@st.cache_resource
def get_db():
    client = boto3.client("secretsmanager", region_name="ap-south-1")
    s = json.loads(client.get_secret_value(SecretId=SECRET_ARN)["SecretString"])
    return mysql.connector.connect(
        host=s["DB_HOST"],
        user=s["DB_USER"],
        password=s["DB_PASSWORD"],
        database=s["DB_NAME"],
    )

# --- Streamlit Rendering Function ---
def render(navigate):
    st.markdown("<div class='page'>", unsafe_allow_html=True)
    col1, col2 = st.columns([2.7, 2], gap="small")

    # LEFT PANEL (Login)
    with col1:
        st.markdown("<div class='left'>", unsafe_allow_html=True)
        st.markdown(
            "<div class='title'>Login to Your<br>Account</div>", # Line break for visual alignment
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='subtitle'>Access your account</div>",
            unsafe_allow_html=True,
        )

        st.markdown("<div class='card-wrapper'>", unsafe_allow_html=True)
        with st.form("login"):
            # These are now styled with the light gray background via CSS
            email = st.text_input("", placeholder="Email")
            
            # Note: Streamlit handles the password input and the eye icon internally.
            # We use CSS to force the custom colors for the button area next to the input.
            password = st.text_input("", placeholder="Password", type="password") 
            
            # The green "Sign In" button is the form submit button
            ok = st.form_submit_button("Sign In")

            if ok:
                try:
                    conn = get_db()
                    cur = conn.cursor(dictionary=True)
                    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
                    user = cur.fetchone()
                    cur.close()
                    conn.close()
                    if user and bcrypt.checkpw(
                        password.encode(), user["password"].encode()
                    ):
                        st.session_state.logged_in = True
                        st.session_state.user_data = user
                        navigate("chatbot")
                    else:
                        st.error("Incorrect email or password.")
                except Exception as e:
                    st.error(f"An error occurred during login.") # Simplified error for production look

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # RIGHT PANEL (Sign Up)
    with col2:
        st.markdown("<div class='right'>", unsafe_allow_html=True)
        
        # Add the decorative banner element using CSS class
        st.markdown("<div class='right-banner'></div>", unsafe_allow_html=True)

        # Content container to adjust alignment
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
            navigate("signup")
            
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
