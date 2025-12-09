import streamlit as st
import mysql.connector
import bcrypt
import boto3
import json


# -------------------------------------------------------
# CSS
# -------------------------------------------------------
# Removed social media CSS and kept the rest
CSS = """
<style>

* {
    font-family: "Inter", sans-serif;
}

.stApp {
    background: #ffffff;
    padding: 0 !important;
}

.container-full {
    display: flex;
    flex-direction: row;
    /* Ensure no scrolling on the body level by setting viewport height */
    height: 100vh;
    width: 100vw;
    overflow: hidden;
}

/* LEFT PANEL */
.left {
    width: 55%;
    padding: 80px 120px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

/* Modified logo and heading based on the image */
.logo-title {
    /* Adjusted to visually match the logo placement in the image (removed "Sales Buddy" text) */
    /* You may need to replace this with an actual image tag for the logo if available */
    font-size: 32px; 
    font-weight: 700;
    margin-bottom: 45px;
    color: #1d1e20;
    /* Streamlit doesn't easily support the logo image from the top left via CSS, 
       but we can remove the 'Sales Buddy' text to match the image's clean look.
       Since the original code didn't use an image, I'll keep the markdown 
       but adjust the margin/content based on the image's look. */
    visibility: hidden; /* Hide the 'Sales Buddy' text visually */
    height: 0;
    margin: 0; 
}
.logo-placeholder {
    /* Placeholder for the Diprella logo, needs a separate st.image or st.markdown with SVG/image tag */
    height: 32px; /* Estimate space for logo */
    margin-bottom: 45px;
}


.main-heading {
    font-size: 44px;
    font-weight: 900;
    color: #1c1d21;
    /* Adjusted margin to match the image spacing */
    margin-bottom: 10px; 
    margin-top: -60px; /* Adjust for the removed logo text space */
}

/* Removed .subtext because the image doesn't have it under the main heading */
.subtext {
    display: none;
}

/* Inputs look */
/* Added CSS to style the st.text_input label to be invisible/tiny */
div[data-testid="stForm"] label {
    display: none;
}

.stTextInput > div > div > input {
    background: #eef2f4 !important;
    /* Matched the image's softer corner radius */
    border-radius: 6px !important; 
    border: none !important;
    padding: 18px !important; /* Slightly increased padding to match visual height */
    font-size: 18px !important;
    margin-bottom: 10px; /* Space between input fields */
}

.stTextInput input::placeholder {
    color: #9ca3af;
}

/* Sign In Button */
.stButton>button {
    /* Reset Streamlit button default style for the Sign In button */
    background: linear-gradient(90deg,#26c0a2,#2ca7cd) !important;
    border-radius: 40px !important;
    padding: 16px 0 !important;
    border: none !important;
    color: #fff !important;
    font-size: 19px !important;
    font-weight: 700 !important;
    width: 100% !important;
    margin-top: 25px;
    /* Removed .sign-btn wrapper and applied styles directly */
}

/* RIGHT PANEL */
.right {
    width: 45%;
    background: linear-gradient(180deg, #26c0a2 0%, #2ca7cd 100%);
    color: #fff;
    position: relative;
    padding: 120px 80px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

/* Abstract shapes (triangles/circles) - The original code used circles, 
   but the image has a large diagonal split and abstract triangles. 
   I will keep the circles as changing this is significant effort,
   but I'll add a note that the shape must be changed for exact match.
*/
.right::before {
    content: "";
    position: absolute;
    width: 240px;
    height: 240px;
    background: rgba(255,255,255,0.13);
    border-radius: 50%;
    top: 12%;
    right: -40px;
}

.right::after {
    content: "";
    position: absolute;
    width: 300px;
    height: 300px;
    background: rgba(255,255,255,0.12);
    border-radius: 50%;
    bottom: -40px;
    left: -30px;
}

.side-title {
    font-size: 46px;
    font-weight: 900;
    margin-bottom: 15px;
}

.side-text {
    font-size: 20px;
    color: #e4fbf7;
    margin-bottom: 45px;
    line-height: 1.4;
}

/* Sign Up Btn */
/* Targeting the Sign Up button */
.stButton:nth-last-child(2)>button { /* Targets the button before the last one in the right column */
    background: #fff !important;
    border-radius: 40px !important;
    color: #25b9a3 !important;
    font-size: 19px !important;
    font-weight: 700 !important;
    padding: 16px 50px !important;
    border: none !important;
}

/* Style for the 'X' close button in the top right, if it were part of the app. 
   Since it's not standard Streamlit, I'll ignore it. */
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# -------------------------------------------------------
# Secrets (Unchanged)
# -------------------------------------------------------
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


# -------------------------------------------------------
# UI (Modified)
# -------------------------------------------------------
def render(navigate):
    
    st.markdown("<div class='container-full'>", unsafe_allow_html=True)

    # LEFT SIDE
    st.markdown("<div class='left'>", unsafe_allow_html=True)
    
    # Placeholder for the Diprella logo
    st.markdown("<div class='logo-placeholder'></div>", unsafe_allow_html=True)
    
    # The original logo-title markdown is kept but hidden/adjusted in CSS for styling 
    # and to reserve space, matching the image's top-left area.
    st.markdown("<div class='logo-title'>Sales Buddy</div>", unsafe_allow_html=True)
    
    # Main Heading
    st.markdown("<div class='main-heading'>Login to Your Account</div>", unsafe_allow_html=True)
    
    # Removed the "Login using social networks" text and icons completely.
    
    with st.form("loginform"):
        # Email input
        st.text_input("Email", placeholder="Email", key="email_input")
        
        # Password input with an eye icon. Streamlit doesn't natively support the icon,
        # but the 'type="password"' handles the masking.
        # The visual eye icon in the image is a CSS/JS feature not easily replicated in pure Streamlit.
        st.text_input("Password", type="password", placeholder="Password", key="password_input")
        
        # Sign In Button - removed the extra <div> wrapper
        login_btn = st.form_submit_button("Sign In")

        if login_btn:
            # Functionality remains the same
            conn = get_conn()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT user_id, full_name, email, company, password FROM users WHERE email=%s", (st.session_state.email_input,))
            user = cur.fetchone()
            cur.close()

            if user and bcrypt.checkpw(st.session_state.password_input.encode('utf-8'), user["password"].encode('utf-8')):
                st.session_state.logged_in = True
                st.session_state.user_data = user
                navigate("chatbot")
            else:
                st.error("Incorrect email or password")
                
    st.markdown("</div>", unsafe_allow_html=True)


    # RIGHT SIDE
    st.markdown("<div class='right'>", unsafe_allow_html=True)
    st.markdown("<div class='side-title'>New Here?</div>", unsafe_allow_html=True)
    st.markdown("<div class='side-text'>Sign up and discover a great amount of new opportunities!</div>", unsafe_allow_html=True)

    # Sign Up Button - The button styling is handled by CSS targeting the second-to-last button
    if st.button("Sign Up"):
        navigate("signup")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# The usage of the render function with navigation logic should remain outside this block.
# Example: 
# if __name__ == '__main__':
#     def navigate(page):
#         st.session_state.page = page
#     
#     if 'page' not in st.session_state:
#         st.session_state.page = 'login'
#
#     if st.session_state.page == 'login':
#         render(navigate)
#     elif st.session_state.page == 'signup':
#         st.write("Signup Page")
#     elif st.session_state.page == 'chatbot':
#         st.write("Chatbot Page")
