import streamlit as st
import mysql.connector
import boto3
import json
import bcrypt 


# --------------------------------------------------------
# -------------------- GLOBAL CSS ------------------------
# --------------------------------------------------------
CSS = """
<style>

.stApp {
    background: #f4f6f9;
}


/* Main Card Container */
.main-container {
    display: flex;
    flex-direction: row;
    width: 900px;
    margin: 60px auto;
    background: #ffffff;
    border-radius: 18px;
    overflow: hidden;
    box-shadow: 0 18px 50px rgba(0,0,0,0.08);
    border: 1px solid #eee;
}


/* LEFT SECTION - Login */
.left-section {
    width: 55%;
    padding: 60px 45px;
}

.login-title {
    font-size: 34px;
    font-weight: 800;
    color: #202936;
    margin-bottom: 8px;
}

.login-subtitle {
    color: #6f7b8a;
    font-size: 17px;
    margin-bottom: 45px;
}


/* RIGHT SECTION - Signup */
.right-section {
    width: 45%;
    padding: 80px 40px;
    background: linear-gradient(135deg, #0fb8ad, #1fc8db, #2cb5e8);
    display: flex;
    flex-direction: column;
    justify-content: center;
    text-align: left;
}

.signup-title {
    font-size: 32px;
    font-weight: 800;
    color: white;
    margin-bottom: 15px;
}

.signup-text {
    font-size: 17px;
    color: #e8f8fa;
    margin-bottom: 35px;
    line-height: 1.5;
}


/* Signup Button */
.signup-btn {
    background: white;
    color: #1e8b92;
    padding: 12px 0;
    border-radius: 50px;
    font-weight: 600;
    width: 220px;
    border: none;
    cursor: pointer;
    font-size: 17px;
}

.signup-btn:hover {
    background: #f6fefe;
}


/* Input fields */
.stTextInput input {
    border-radius: 10px !important;
    border: 1px solid #ccd3dc !important;
    padding: 12px 14px !important;
    font-size: 16px !important;
}

.stTextInput input:focus {
    border-color: #1abc9c !important;
    box-shadow: 0px 0px 0px 3px rgba(26, 188, 156, 0.25) !important;
}


/* Login Button */
.stForm button {
    background-color: #16a085 !important;
    width: 100%;
    color: white !important;
    font-size: 18px !important;
    border-radius: 8px !important;
    padding: 12px 0px !important;
    border: none !important;
}

.stForm button:hover {
    background-color: #118b73 !important;
}


/* Links Section */
.link-row {
    margin-top: 25px;
    display: flex;
    justify-content: space-between;
}

.link-btn {
    background: none !important;
    color: #118b73 !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    border: none !important;
}

.link-btn:hover {
    text-decoration: underline;
}

</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# --------------------------------------------------------
# -------------------- AWS SECRETS -----------------------
# --------------------------------------------------------
SECRET_ARN = "arn:aws:secretsmanager:ap-south-1:034362058776:secret:salesbuddy/secrets-0xh2TS"

@st.cache_resource
def get_db_secrets():
    try:
        client = boto3.client("secretsmanager", region_name="ap-south-1")
        resp = client.get_secret_value(SecretId=SECRET_ARN)
        raw = json.loads(resp["SecretString"])
        return {
            "DB_HOST": raw["DB_HOST"],
            "DB_USER": raw["DB_USER"],
            "DB_PASSWORD": raw["DB_PASSWORD"],
            "DB_NAME": raw["DB_NAME"]
        }
    except Exception as e:
        raise RuntimeError(f"Failed to load DB secrets: {e}")


@st.cache_resource
def get_conn():
    try:
        creds = get_db_secrets()
        conn = mysql.connector.connect(
            host=creds["DB_HOST"],
            user=creds["DB_USER"],
            password=creds["DB_PASSWORD"],
            database=creds["DB_NAME"],
            charset="utf8mb4"
        )
        return conn
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        st.stop()


# --------------------------------------------------------
# -------------------- LOGIN UI --------------------------
# --------------------------------------------------------
def render(navigate):

    st.markdown("<div class='main-container'>", unsafe_allow_html=True)


    # ---------------- LEFT: LOGIN ----------------
    st.markdown("<div class='left-section'>", unsafe_allow_html=True)

    st.markdown("<h2 class='login-title'>Login to Your Account</h2>", unsafe_allow_html=True)
    st.markdown("<p class='login-subtitle'>Enter your email & password to continue</p>", unsafe_allow_html=True)

    with st.form(key="login_form"):
        email = st.text_input("Email", placeholder="you@company.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submitted = st.form_submit_button("Sign In")

        if submitted:
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                try:
                    conn = get_conn()
                    cur = conn.cursor(dictionary=True)
                    cur.execute("SELECT user_id, full_name, email, company, password FROM users WHERE email=%s", (email,))
                    user_record = cur.fetchone()
                    cur.close()

                    if user_record and bcrypt.checkpw(password.encode('utf-8'), user_record['password'].encode('utf-8')):
                        st.session_state.logged_in = True
                        st.session_state.user_data = {
                            "user_id": user_record["user_id"],
                            "full_name": user_record["full_name"],
                            "email": user_record["email"],
                            "company": user_record["company"]
                        }
                        st.success("Login successful...")
                        navigate("chatbot")
                    else:
                        st.error("Incorrect email or password.")
                except Exception as e:
                    st.error(f"Login failed: {e}")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Forgot Password?", key="fp-btn", use_container_width=True):
            navigate("forgot_password")
    with c2:
        if st.button("Sign Up", key="su-btn", use_container_width=True):
            navigate("signup")

    st.markdown("</div>", unsafe_allow_html=True)



    # ---------------- RIGHT: SIGNUP INFO ----------------
    st.markdown("<div class='right-section'>", unsafe_allow_html=True)

    st.markdown("<h2 class='signup-title'>New Here?</h2>", unsafe_allow_html=True)

    st.markdown("""
        <p class='signup-text'>
            <b>Sales Buddy</b> is your AI-powered sales assistant,
            built to help you manage leads, automate follow-ups,
            track conversations, and close deals faster.
            <br><br>
            Discover smart analytics, deal pipeline tracking and
            personalized recommendations to scale your sales performance.
        </p>
    """, unsafe_allow_html=True)

    if st.button("Create Your Account", key="create-btn", help="", args=None):
        navigate("signup")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
