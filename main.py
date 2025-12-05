import streamlit as st
import login
import signup
import forgot_password
import chatbot

# --------------------------------------------------------
# ------------------ CONFIGURATION -----------------------
# --------------------------------------------------------
# Use 'wide' layout for the main app for flexibility
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
    # Initialize with default structure
    st.session_state.user_data = {"full_name": "Guest User", "email": ""} 
    
# 🆕 Initialize the chat history (used by chatbot.py)
if "chat" not in st.session_state:
    st.session_state.chat = [{"role": "ai", "content": "Hello! I have loaded your CRM data. Ask me anything about your leads using the examples below!"}]

# 🆕 Initialize the chat status flag (used by chatbot.py to switch views)
if "chat_initiated" not in st.session_state:
    st.session_state.chat_initiated = False


def navigate(page):
    """
    Sets the new page state and clears the resource cache if navigating 
    away from authentication pages to ensure fresh DB connection on the next run.
    """
    # Clear cache when moving away from authentication to prevent stale DB connections
    if st.session_state.page in ["login", "signup", "forgot_password"] and page not in ["login", "signup", "forgot_password"]:
        st.cache_resource.clear()
        
    st.session_state.page = page
    st.rerun() # Force Streamlit to re-run the script immediately

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
        # ✅ FIX: Pass the required 'user_data' from session state
        chatbot.render(navigate, st.session_state.user_data) 
    else:
        # If somehow they jumped here without logging in, send them back
        st.warning("Please log in to access the chatbot.")
        navigate("login")
