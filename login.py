import streamlit as st
import mysql.connector
import bcrypt
import base64

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(
    page_title="Sales Buddy | Login",
    layout="wide"
)

# ----------------------------------
# BACKGROUND IMAGE FUNCTION
# ----------------------------------
def set_background(image_path: str):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    st.markdown(
        f"""
        <style>
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

# ----------------------------------
# APPLY BACKGROUND
# ----------------------------------
set_background("images/bg.jpg")

# ----------------------------------
# GLOBAL CSS (MATCHES YOUR DASHBOARD)
# ----------------------------------
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');

* {
    font-family: 'Poppins', sans-serif !important;
}

/* Hide Streamlit toolbar/header/footer */
.stApp > header, .stApp > footer {
    display:none !important;
}
[data-testid="stToolbar"] {
    background: transparent !important;
}

/* Full Layout Wrapper */
.wrapper {
    height:100vh;
    display:flex;
    flex-direction:row;
    overflow:hidden;
}

/* Left panel */
.left-panel {
    flex:1;
    display:flex;
    flex-direction:column;
    justify-content:center;
    padding:80px;
}

/* Title text */
.login-title {
    font-size:48px;
    font-weight:800;
    margin-bottom:10px;
    color:white;
}
.login-sub {
    font-size:18px;
    margin-bottom:35px;
    color:white;
}

/* Dark Card Style for Inputs */
.form-box {
    background-color: rgba(0,0,0,0.70);
    backdrop-filter: blur(6px);
    padding: 40px;
    border-radius: 18px;
    width: 450px;
    box-shadow: 0 8px 16px rgba(0,0,0,0.35);
}

/* Inputs */
.stTextInput > div > div > input {
    background:#1a1a1a !important;
    color:white !important;
    border: 1px solid #555 !important;
    border-radius:12px !important;
    padding:14px !important;
}

/* Buttons */
form button, .stButton > button {
    background:#00b894 !important;
    color:white !important;
    font-weight:700 !important;
    font-size:18px !important;
    border:none !important;
    border-radius:12px !important;
    padding:14px !important;
    margin-top:10px;
    width:100% !important;
}

/* Right panel */
.right-panel {
    flex:1;
    display:flex;
    flex-direction:column;
    justify-content:center;
    padding:80px;
    background:rgba(0,0,0,0.35);
    border-left: 1px solid rgba(255,255,255,0.25);
    backdrop-filter: blur(6px);
    text-align:left;
}

.right-title {
    font-size:46px;
    font-weight:800;
    color:white;
    margin-bottom:15px;
}
.right-text {
    font-size:19px;
    color:white;
    max-width:330px;
    margin-bottom:35px;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------------
# DATABASE
# ----------------------------------
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="salesbuddy"
    )

# ----------------------------------
# LOGIN UI
# ----------------------------------
def render(navigate):
    
    st.markdown("<div class='wrapper'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1,1])

    # LEFT PANEL
    with col1:
        st.markdown("<div class='left-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='login-title'>Login to Your<br>Account</div>", unsafe_allow_html=True)
        st.markdown("<div class='login-sub'>Access your account</div>", unsafe_allow_html=True)

        st.markdown("<div class='form-box'>", unsafe_allow_html=True)
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign In")

            if submit:
                try:
                    conn = get_db()
                    cur = conn.cursor(dictionary=True)
                    cur.execute("SELECT * FROM users WHERE email=%s",(email,))
                    user = cur.fetchone()
                    cur.close()

                    if user and bcrypt.checkpw(password.encode(),user["password"].encode()):
                        st.session_state.logged_in = True
                        st.session_state.user_data = user
                        navigate("dashboard")
                    else:
                        st.error("Incorrect email or password")
                except Exception as e:
                    st.error("Login failed")
                    st.error(e)

        st.markdown("</div>", unsafe_allow_html=True)

    # RIGHT PANEL
    with col2:
        st.markdown("<div class='right-panel'>", unsafe_allow_html=True)
        
        st.markdown("<div class='right-title'>New Here?</div>", unsafe_allow_html=True)
        st.markdown("<div class='right-text'>Sign up and discover a great amount of new opportunities!</div>", unsafe_allow_html=True)

        if st.button("Sign Up"):
            navigate("signup")

    # Close wrapper
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------
# LOCAL TEST
# ----------------------------------
if __name__ == "__main__":
    def go(x): st.success(f"Navigate → {x}")
    render(go)
