import streamlit as st
import mysql.connector

# CSS included directly
CSS = """
<style>
.login-box {
    background: #ffffff;
    width: 420px;
    padding: 40px;
    margin: auto;
    margin-top: 50px;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.center { text-align:center; }
a { color: green; text-decoration:none; }
button { border-radius:8px !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# MySQL connection
def get_conn():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="yourpwd",
        database="smart_chatbot_db"
    )

def render(navigate):

    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/149/149071.png", width=70)
    st.markdown("<h2 class='center'>Welcome Back</h2>", unsafe_allow_html=True)
    st.markdown("<p class='center'>Sign in to Smart Chatbot</p>", unsafe_allow_html=True)

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns([1, 1])
    remember = col1.checkbox("Remember me")

    forgot_html = "<a href='#' onclick='window.location=\"/?fp=1\";'>Forgot password?</a>"
    col2.markdown(forgot_html, unsafe_allow_html=True)

    if st.button("Log In", use_container_width=True):
        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()

        if user and user["password"] == password:
            st.success("Login Success!")
            navigate("chatbot")
        else:
            st.error("Incorrect Email or Password")

        conn.close()

    st.markdown("""
        <br>
        <p class='center'>Don't have an account? 
        <a href='#' onclick='window.location="/?su=1"'>Sign up</a></p>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # URL navigation override
    params = st.query_params
    if "su" in params:
        navigate("signup")
    if "fp" in params:
        navigate("forgot_password")
