import streamlit as st
import login
import signup
import forgot_password
import chatbot

st.set_page_config(page_title="Smart Chatbot", page_icon="🤖", layout="centered")

# session state navigation
if "page" not in st.session_state:
    st.session_state.page = "login"

def navigate(page):
    st.session_state.page = page

# navigation router
if st.session_state.page == "login":
    login.render(navigate)

elif st.session_state.page == "signup":
    signup.render(navigate)

elif st.session_state.page == "forgot_password":
    forgot_password.render(navigate)

elif st.session_state.page == "chatbot":
    chatbot.render(navigate)
