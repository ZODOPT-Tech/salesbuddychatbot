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
    box-sizing:border-box;
}

.stApp > header, .stApp > footer {
    display:none;
}

/* Ensure the main container takes full viewport height and remove default padding/margin */
.stApp > main .block-container {
    padding:0 !important;
    margin:0 !important;
    max-width: 100% !important; /* Important for wide layout */
    min-height: 100vh; /* Ensure full height */
}

/* full page wrapper */
.page {
    width:100vw;
    height:100vh;
    overflow:hidden; /* Prevents scrolling */
    display: flex;
}

/* make columns full height */
/* The block that holds st.columns */
[data-testid="stHorizontalBlock"] {
    height:100%;
    width: 100%;
}

/* LEFT PANEL */
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

/* form card */
.card {
    width:420px;
    background:#ffffff;
    border-radius:18px;
    padding:0; /* Removed padding here as it's not needed for the card wrapper */
    /* box-shadow:0 18px 45px rgba(40,56,120,0.08); Removed to simplify the look */
}

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

form button {
    background:#20c997 !important;
    color:#ffffff !important;
    border:none !important;
    border-radius:35px !important;
    padding:12px 0 !important;
    font-weight:700 !important;
    font-size:17px !important;
    width:100% !important;
    margin-top:12px;
}

/* RIGHT PANEL – gradient background */
.right {
    height:100%;
    /* Gradient color adjusted to better match the visual style of the image's background */
    background:linear-gradient(135deg, #00A6D9 0%, #008BD5 50%, #1CCABF 100%);
    display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:flex-start;
    color:#ffffff;
    position:relative;
    padding: 70px; /* Keep padding for content spacing */
    overflow: hidden; /* Important for the pseudo-elements */
}

/* Removed decorative circles as they weren't in the reference image's simplified right panel */

.brand {
    font-size:28px;
    font-weight:700;
    margin-bottom:40px;
    z-index:5;
}

.nh {
    font-size:46px;
    font-weight:800;
    margin-bottom:10px;
    z-index:5;
}

.desc {
    font-size:18px;
    max-width:330px;
    margin-bottom:35px;
    color:#e8fbf8;
    z-index:5;
}

.right .stButton > button {
    background:#ffffff !important;
    color:#15b7a5 !important;
    font-weight:700 !important;
    border-radius:35px !important;
    padding:14px 40px !important;
    border:none !important;
    font-size:18px !important;
    z-index:10;
}

/* Custom element to act as the decorative shape/banner on the right side */
.right-banner {
    position: absolute;
    top: 60px; /* Position it high up */
    right: 50px; /* Position it to the right */
    width: 300px; /* Adjust size */
    height: 100px; /* Adjust size */
    /* Use a similar but simpler gradient/color to mimic the shape */
    background: linear-gradient(90deg, #1CCABF, #00A6D9);
    border-radius: 10px;
    /* Apply a slight skew/transform if desired for a more dynamic look */
    /* transform: skewY(-2deg); */ 
    z-index: 1; /* Keep it below text */
}

/* Overriding the text color for the 'New Here?' section to match the light grey in the image */
.right .nh {
    font-size: 56px; /* Increased for better visual weight */
}

.right .desc {
    color: #ffffff; /* Keeping description white for contrast */
    font-size: 16px;
    font-weight: 400;
}

/* Adjusting the content display for the right panel to match the screenshot */
.right-content {
    display: flex;
    flex-direction: column;
    justify-content: center;
    height: 100%;
    z-index: 5; /* Ensure content is above the banner */
    margin-top: -150px; /* Nudge up content to align with the image's layout */
}

</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

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

def render(navigate):
    # The 'page' div now correctly wraps the full content
    st.markdown("<div class='page'>", unsafe_allow_html=True) 
    col1, col2 = st.columns([2.7, 2], gap="small")

    # LEFT PANEL
    with col1:
        st.markdown("<div class='left'>", unsafe_allow_html=True)
        st.markdown(
            "<div class='title'>Login to Your Account</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='subtitle'>Access your account</div>",
            unsafe_allow_html=True,
        )

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        with st.form("login"):
            email = st.text_input("", placeholder="Email")
            password = st.text_input("", placeholder="Password", type="password")
            # Removed the password visibility icon in the Python code for a cleaner look
            ok = st.form_submit_button("Sign In")

            if ok:
                try:
                    conn = get_db()
                    cur = conn.cursor(dictionary=True)
                    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
                    user = cur.fetchone()
                    cur.close()
                    conn.close() # Always close connection
                    if user and bcrypt.checkpw(
                        password.encode(), user["password"].encode()
                    ):
                        st.session_state.logged_in = True
                        st.session_state.user_data = user
                        navigate("chatbot")
                    else:
                        st.error("Incorrect email or password.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # RIGHT PANEL
    with col2:
        st.markdown("<div class='right'>", unsafe_allow_html=True)
        
        # Add the decorative banner element using CSS class
        st.markdown("<div class='right-banner'></div>", unsafe_allow_html=True)

        # Content container to adjust alignment
        st.markdown("<div class='right-content'>", unsafe_allow_html=True)
        
        # Display the brand name (Sales Buddy) and the login prompt.
        # This will now be overlaid on the gradient background.
        st.markdown("<div class='brand'>Sales Buddy</div>", unsafe_allow_html=True)
        st.markdown("<div class='nh'>New Here?</div>", unsafe_allow_html=True)
        
        # Use a div with a custom style to match the light-grey-on-gradient effect of the image
        st.markdown(
            """
            <div class='desc' style='color:#e8fbf8;'>
                Sign up and discover a great amount of new opportunities!
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        # Sign Up button
        if st.button("Sign Up"):
            navigate("signup")
            
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
