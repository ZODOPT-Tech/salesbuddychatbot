import streamlit as st
import mysql.connector

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
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

def get_conn():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="yourpwd",
        database="smart_chatbot_db"
    )

def render(navigate):

    st.markdown("<div class='forgot-box'>", unsafe_allow_html=True)

    st.image("https://cdn-icons-png.flaticon.com/512/149/149071.png", width=70)
    st.markdown("<h2 class='center'>Reset Password</h2>", unsafe_allow_html=True)

    email = st.text_input("Enter Your Registered Email")

    if st.button("Send Reset Link", use_container_width=True):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email=%s", (email,))
        user = cur.fetchone()

        if user:
            st.success("Password reset link sent to your email!")
        else:
            st.error("Email does not exist")

        conn.close()

    if st.button("Back to Login", use_container_width=True):
        navigate("login")

    st.markdown("</div>", unsafe_allow_html=True)
