import streamlit as st
import mysql.connector
import boto3
import json
import bcrypt # For hashing the new password (pip install bcrypt)

# --------------------------------------------------------
# -------------------- CSS (Green Theme) ------------------
# --------------------------------------------------------
CSS = """
<style>
.forgot-box {
    background: #ffffff;
    width: 420px;
    padding: 40px;
    margin: auto;
    margin-top: 60px;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.center { text-align:center; }
/* Style the primary button */
div[data-testid="stForm"] button { 
    background-color: #28a745 !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
    width: 100% !important;
    padding: 10px !important;
    margin-top: 15px;
}
div[data-testid="stForm"] button:hover {
    background-color: #1f7a38 !important;
}
/* Style the back button */
div.stButton button { 
    background-color: #6c757d !important; /* Gray */
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
    width: 100% !important;
    padding: 10px !important;
    margin-top: 10px;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# --------------------------------------------------------
# ---------------- AWS Secrets Manager --------------------
# --------------------------------------------------------
SECRET_ARN = "arn:aws:secretsmanager:ap-south-1:034362058776:secret:salesbuddy/secrets-0xh2TS"

@st.cache_resource
def get_db_secrets():
    """Fetch DB credentials from AWS Secrets Manager."""
    try:
        client = boto3.client("secretsmanager", region_name="ap-south-1")
        resp = client.get_secret_value(SecretId=SECRET_ARN)
        raw = json.loads(resp["SecretString"])
        return {
            "DB_HOST": raw["DB_HOST"], "DB_USER": raw["DB_USER"],
            "DB_PASSWORD": raw["DB_PASSWORD"], "DB_NAME": raw["DB_NAME"]
        }
    except Exception as e:
        st.error(f"Configuration Error: Failed to load DB secrets: {e}")
        st.stop()


# --------------------------------------------------------
# ------------------ MYSQL CONNECTION ---------------------
# --------------------------------------------------------
@st.cache_resource
def get_conn():
    """Connect to MySQL using AWS secrets."""
    try:
        creds = get_db_secrets()
        conn = mysql.connector.connect(
            host=creds["DB_HOST"], user=creds["DB_USER"],
            password=creds["DB_PASSWORD"], database=creds["DB_NAME"],
            charset="utf8mb4"
        )
        return conn
    except mysql.connector.Error as e:
        st.error(f"Database Connection Error: {e}")
        st.stop()

# --------------------------------------------------------
# ------------------ FORGOT PASSWORD RENDER ---------------
# --------------------------------------------------------

# Initialize session state for the reset email
if "reset_email" not in st.session_state:
    st.session_state.reset_email = None

def render(navigate):
    
    st.markdown("<div class='forgot-box'>", unsafe_allow_html=True)
    st.markdown("<div class='center'>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/149/149071.png", width=70)
    st.markdown("<h2 class='center'>Reset Password</h2>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # --- STEP 1: Enter Email ---
    if st.session_state.reset_email is None:
        
        st.markdown("<p class='center'>Enter your email address to verify your account.</p>", unsafe_allow_html=True)

        with st.form(key='verify_email_form'):
            email = st.text_input("Enter Your Registered Email", placeholder="email@company.com", key="reset_email_input")
            submitted = st.form_submit_button("Verify Email", use_container_width=True)

            if submitted:
                if not email:
                    st.error("Please enter your email address.")
                    st.stop()
                
                try:
                    conn = get_conn()
                    cur = conn.cursor()
                    cur.execute("SELECT id FROM users WHERE email=%s", (email,))
                    user = cur.fetchone()

                    if user:
                        st.session_state.reset_email = email
                        st.rerun() # Move to the password reset step
                    else:
                        st.error("Email not found. Please check your address.")

                    cur.close()
                except Exception as e:
                    st.error(f"Error during verification: {e}")

    # --- STEP 2: Change Password ---
    else:
        st.markdown(f"<p class='center'>Changing password for <b>{st.session_state.reset_email}</b>.</p>", unsafe_allow_html=True)
        
        with st.form(key='reset_password_form'):
            new_password = st.text_input("New Password", type="password", placeholder="Enter new password")
            confirm_new_password = st.text_input("Confirm New Password", type="password", placeholder="Confirm new password")
            
            submitted = st.form_submit_button("Reset Password", use_container_width=True)

            if submitted:
                if not new_password or not confirm_new_password:
                    st.error("Both password fields are required.")
                elif new_password != confirm_new_password:
                    st.error("Passwords do not match!")
                else:
                    try:
                        # HASH the new password
                        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                        hashed_password_str = hashed_password.decode('utf-8')
                        
                        conn = get_conn()
                        cur = conn.cursor()
                        
                        # Update the user's password using the stored email
                        update_query = "UPDATE users SET password = %s WHERE email = %s"
                        cur.execute(update_query, (hashed_password_str, st.session_state.reset_email))
                        conn.commit()
                        cur.close()

                        st.success("Your password has been successfully reset! Redirecting to login...")
                        
                        # Clear the session state variable and navigate back
                        st.session_state.reset_email = None 
                        navigate("login")

                    except Exception as e:
                        st.error(f"Error during password reset: {e}")

    # --- Back to Login Button ---
    if st.button("Back to Login", use_container_width=True, key='back_to_login_btn'):
        st.session_state.reset_email = None # Clear reset state on navigation
        navigate("login")

    st.markdown("</div>", unsafe_allow_html=True)
