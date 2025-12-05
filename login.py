import streamlit as st
import mysql.connector

# --------------------------------------------------------
# -------------------- PROFESSIONAL CSS -------------------
# --------------------------------------------------------
CSS = """
<style>

body {
    background-color: #f5f7fa;
}

/* LOGIN CARD */
.login-card {
    background: #ffffff;
    width: 420px;
    padding: 40px;
    margin: auto;
    margin-top: 60px;
    border-radius: 18px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.08);
    border: 1px solid #e6e6e6;
}

/* HEADER */
.title-header {
    font-size: 30px;
    font-weight: 700;
    color: #222;
    margin-bottom: 5px;
}

.subtitle {
    font-size: 16px;
    color: #666;
    margin-bottom: 25px;
}

/* TEXT INPUTS */
.stTextInput > label {
    display: none;
}

.stTextInput input {
    border-radius: 10px !important;
    border: 1px solid #cccccc !important;
    padding: 12px 14px !important;
    font-size: 16px !important;
}

.stTextInput input:focus {
    border-color: #28a745 !important;
    box-shadow: 0px 0px 0px 2px rgba(40, 167, 69, 0.25) !important;
}

/* MAIN LOGIN BUTTON */
.stButton>button {
    background-color: #28a745 !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 12px !important;
    border: none !important;
    font-size: 18px !important;
    font-weight: 600 !important;
    transition: background-color 0.3s ease;
}

.stButton>button:hover {
    background-color: #1f7a38 !important;
}

/* LINK BUTTON STYLE */
.action-link {
    background: none !important;
    border: none !important;
    color: #28a745 !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    padding: 0 !important;
    margin: 0 !important;
    font-size: 15px !important;
}

.action-link:hover {
    text-decoration: underline !important;
    color: #1f7a38 !important;
}

/* Bottom row links container */
.bottom-links {
    display: flex;
    justify-content: center;
    gap: 25px;
    margin-top: 25px;
}

</style>
"""

st.markdown(CSS, unsafe_allow_html=True)



# --------------------------------------------------------
# ------------------ MYSQL CONNECTION ---------------------
# --------------------------------------------------------
def get_conn():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="yourpwd",
        database="smart_chatbot_db"
    )



# --------------------------------------------------------
# ------------------ LOGIN RENDER FUNCTION ----------------
# --------------------------------------------------------
def render(navigate):

    st.markdown("<div class='login-card'>", unsafe_allow_html=True)

    # ---------------- HEADER ----------------
    st.markdown("""
        <div style='text-align:center;'>
            <img src="https://cdn-icons-png.flaticon.com/512/149/149071.png"
            width="70"
            style="background-color:#28a745; border-radius:50%; padding:10px;">
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<h2 class='title-header' style='text-align:center;'>SalesBuddy Login</h2>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle' style='text-align:center;'>Access your account</p>", unsafe_allow_html=True)

    # ---------------- INPUT FIELDS ----------------
    email = st.text_input("Email", placeholder="your.email@company.com", key="email_login")
    password = st.text_input("Password", type="password", placeholder="Enter your password", key="password_login")

    # ---------------- REMEMBER ME ----------------
    st.checkbox("Remember me", value=True, key="remember_me")

    # ---------------- LOGIN BUTTON ----------------
    if st.button("Log In", use_container_width=True, key="login_button"):
        try:
            conn = get_conn()
            cur = conn.cursor(dictionary=True)

            cur.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cur.fetchone()

            if user and user["password"] == password:
                st.success("Login successful! Redirecting...")
                navigate("chatbot")
            else:
                st.error("Incorrect email or password")

            conn.close()

        except Exception as e:
            st.error(f"Error: {e}")

    # ---------------- FORGOT + SIGNUP (CENTERED, SAME LINE) ----------------
    st.markdown("""
        <div class='bottom-links'>
            <button class='action-link' id='fp-btn'>Forgot Password?</button>
            <button class='action-link' id='su-btn'>Sign Up</button>
        </div>
    """, unsafe_allow_html=True)

    # JS trigger for our links
    st.markdown("""
        <script>
        document.getElementById('fp-btn').onclick = function() {
            window.parent.postMessage({type:'streamlit:setComponentValue', value:'fp'}, '*');
        };
        document.getElementById('su-btn').onclick = function() {
            window.parent.postMessage({type:'streamlit:setComponentValue', value:'su'}, '*');
        };
        </script>
    """, unsafe_allow_html=True)

    # Handle custom triggers
    if "streamlit:setComponentValue" in st.session_state:
        if st.session_state["streamlit:setComponentValue"] == "fp":
            navigate("forgot_password")
        if st.session_state["streamlit:setComponentValue"] == "su":
            navigate("signup")

    st.markdown("</div>", unsafe_allow_html=True)
