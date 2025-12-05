import streamlit as st

def render(navigate):
    st.title("🤖 Smart Chatbot")
    st.write("Welcome! You are logged in.")

    query = st.text_input("Ask something...")
    if query:
        st.write("AI Response (coming soon...)")

    if st.button("Logout"):
        navigate("login")
