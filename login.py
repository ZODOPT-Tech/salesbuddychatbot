import streamlit as st
import mysql.connector
import boto3
import json
import bcrypt 

# --------------------------------------------------------
# -------------------- CSS (Snippet for Login) -------------------
# --------------------------------------------------------
CSS = """
<style>
/* Streamlit main background */
.stApp { background-color: #f5f7fa; }
/* LOGIN CARD */
.login-card {
    background: #ffffff; width: 420px; padding: 40px; margin: auto;
    margin-top: 60px; border-radius: 18px; box-shadow: 0 8px 30px rgba(0,0,0,0.08);
    border: 1px solid #e6e6e6;
}
.title-header { font-size: 30px; font-weight: 700; color: #222; margin-bottom: 5px; }
.subtitle { font-size: 16px; color: #666; margin-bottom: 25px; }
/* Text Inputs */
.stTextInput > label { display: none; }
.stTextInput input { border-radius: 10px !important; border: 1px solid #cccccc !important; padding: 12px 14px !important; font-size: 16px !important; }
.stTextInput input:focus { border-color: #28a745 !important; box-shadow: 0px 0px 0px 2px rgba(40, 167, 69, 0.25) !important; }
/* Primary Button */
div[data-testid="stForm"] > div > div:nth-child(4) > div > div > button { 
    background-color: #28a745 !important; color: white !important; border-radius: 8px !important;
    padding: 12px !important; border: none !important; font-size: 18px !important;
    font-weight: 600 !important; width: 100%;
}
/* Bottom links */
.bottom-links { margin-top: 25px; display: flex; justify-content: space-between; gap: 10px; }
.action-link-button { 
    background-color: transparent !important; color: #28a745 !important; border: none !important;
    font-weight: 600 !important; cursor: pointer !important; padding: 10px 0 !important; 
    font-size: 15px !important; text-align: center; width: 100% !important;
}
.action-link-button:hover { text-decoration: underline !important; background-color: transparent !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# --------------------------------------------------------
# ---------------- AWS SECRETS CONFIGURATION --------------
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
        raise RuntimeError(f"Failed to connect to AWS Secrets Manager: {e}")

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

    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        st.stop()


# --------------------------------------------------------
# ------------------ LOGIN RENDER FUNCTION ----------------
# --------------------------------------------------------
def render(navigate):
    """Renders the login form and handles authentication."""

    with st.container():
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)

        # ---------------- HEADER ----------------
        st.markdown("""
            <div style='text-align:center;'>
                <img src="https://cdn-icons-png.flaticon.com/512/149/149071.png"
                width="70" style="background-color:#28a745; border-radius:50%; padding:10px;">
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<h2 class='title-header' style='text-align:center;'>Welcome to Sales Buddy</h2>", unsafe_allow_html=True)
        st.markdown("<p class='subtitle' style='text-align:center;'>Access your account</p>", unsafe_allow_html=True)

        with st.form(key='login_form'):
            email = st.text_input("Email", placeholder="your.email@company.com", key="email_login")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="password_login")
            st.checkbox("Remember me", value=True, key="remember_me")
            
            submitted = st.form_submit_button("Log In", use_container_width=True, key="login_button_submit")

            if submitted:
                if not email or not password:
                    st.error("Please enter both email and password.")
                else:
                    try:
                        conn = get_conn()
                        # Fetch all necessary data for session, using user_id as PK
                        cur = conn.cursor(dictionary=True) 
                        cur.execute("SELECT user_id, full_name, email, company, password FROM users WHERE email=%s", (email,))
                        user_record = cur.fetchone()
                        cur.close()

                        if user_record:
                            stored_hash = user_record["password"].encode('utf-8')
                            
                            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                                
                                # 🔑 Set Session State for Login 
                                st.session_state.logged_in = True
                                st.session_state.user_data = {
                                    "user_id": user_record["user_id"],
                                    "full_name": user_record["full_name"],
                                    "email": user_record["email"],
                                    "company": user_record["company"]
                                }

                                st.success("Login successful! Redirecting to Chatbot...")
                                navigate("chatbot") 
                            else:
                                st.error("Incorrect email or password")
                        else:
                            st.error("Incorrect email or password")

                    except Exception as e:
                        st.error(f"Unexpected Error during login: {e}") 

        # ---------------- FORGOT + SIGNUP LINKS ----------------
        st.markdown("<div class='bottom-links'>", unsafe_allow_html=True)
        col_fp, col_su = st.columns(2)
        
        with col_fp:
            if st.button("Forgot Password?", key="fp-btn-stable"):
                navigate("forgot_password")
        
        with col_su:
            if st.button("Sign Up", key="su-btn-stable"):
                navigate("signup")
                
        st.markdown("</div>", unsafe_allow_html=True)
        
        # --- CSS Styling Application Hack ---
        st.markdown("""
            <script>
            var buttons = window.parent.document.querySelectorAll('div[data-testid="stColumn"] button');
            buttons.forEach(function(button) {
                var text = button.innerText.trim();
                if (text === 'Forgot Password?' || text === 'Sign Up') {
                    button.classList.add('action-link-button');
                }
            });
            </script>
        """, unsafe_allow_html=True)


        st.markdown("</div>", unsafe_allow_html=True)
