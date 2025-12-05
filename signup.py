import streamlit as st
import mysql.connector

CSS = """
<style>
.signup-box {
    background: #ffffff;
    width: 420px;
    padding: 40px;
    margin: auto;
    margin-top: 50px;
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
    st.markdown("<div class='signup-box'>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/149/149071.png", width=70)

    st.markdown("<h2 class='center'>Create Account</h2>", unsafe_allow_html=True)
    st.markdown("<p class='center'>Join Smart Chatbot today</p>", unsafe_allow_html=True)

    full_name = st.text_input("Full Name")
    email = st.text_input("Email")
    mobile = st.text_input("Mobile Number")
    password = st.text_input("Password", type="password")

    if st.button("Sign Up", use_container_width=True):

        if not (full_name and email and mobile and password):
            st.error("All fields are required")
        else:
            conn = get_conn()
            cur = conn.cursor()

            cur.execute("INSERT INTO users(full_name, email, mobile, password) VALUES (%s,%s,%s,%s)",
                        (full_name, email, mobile, password))
            conn.commit()
            conn.close()

            st.success("Account Created Successfully!")
            navigate("login")

    st.markdown("</div>", unsafe_allow_html=True)
