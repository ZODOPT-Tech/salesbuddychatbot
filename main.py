import streamlit as st
import login
import signup
import forgot_password
import chatbot

# --------------------------------------------------------
# ------------------ CONFIGURATION -----------------------
# --------------------------------------------------------
st.set_page_config(page_title="Sales Buddy Chatbot", page_icon="🤖", layout="wide") 

# --------------------------------------------------------
# ----------------- SESSION STATE & NAVIGATION -----------
# --------------------------------------------------------
# Initialize all necessary session state variables centrally

# Primary page routing
if "page" not in st.session_state:
    st.session_state.page = "login"

# For multi-step password reset flow (used by forgot_password.py)
if "reset_email" not in st.session_state:
    st.session_state.reset_email = None
    
# For user authentication status (used by login.py and chatbot.py)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    
# Store user details upon successful login
if "user_data" not in st.session_state:
    st.session_state.user_data = {"full_name": "Guest User", "email": ""} 
    
# Initialize the chat history (used by chatbot.py)
if "chat" not in st.session_state:
    st.session_state.chat = [
        {"role": "ai", "content": "Hello! I have loaded your CRM data. What would you like to know about Acme Corporation?", "timestamp": "09:00 AM"}
    ]

# 🔑 FIX 1: Initialize the target_lead dictionary used by chatbot.py
if "target_lead" not in st.session_state:
    st.session_state.target_lead = {
        "name": "Acme Corporation",
        "score": "0%",
        "status": "Qualification"
    }
    
# 🔑 FIX 2: Define ACTION_CHIPS as a constant (or initialize in session state if they need to change)
# Since they are static, we define them here globally or keep the constant definition in chatbot.py
ACTION_CHIPS = ["Qualification", "Needs Analysis", "Proposal/Price Quote", "Negotiation/Review", "Closed Won"]


def navigate(page):
    """
    Sets the new page state and clears the resource cache if navigating 
    away from authentication pages to ensure fresh DB connection on the next run.
    """
    if st.session_state.page in ["login", "signup", "forgot_password"] and page not in ["login", "signup", "forgot_password"]:
        st.cache_resource.clear()
        
    st.session_state.page = page
    st.rerun()

# --------------------------------------------------------
# ------------------- NAVIGATION ROUTER ------------------
# --------------------------------------------------------

if st.session_state.page == "login":
    login.render(navigate)

elif st.session_state.page == "signup":
    signup.render(navigate)

elif st.session_state.page == "forgot_password":
    forgot_password.render(navigate)

elif st.session_state.page == "chatbot":
    # Check if the user is authenticated before showing the chatbot
    if st.session_state.logged_in:
        # Pass the ACTION_CHIPS list to the render function as well, 
        # as it's used to build the UI elements.
        chatbot.render(navigate, st.session_state.user_data, ACTION_CHIPS)
    else:
        st.warning("Please log in to access the chatbot.")
        navigate("login")
