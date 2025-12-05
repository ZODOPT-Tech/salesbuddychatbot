import streamlit as st
import login
import signup
import forgot_password
import chatbot

# --------------------------------------------------------
# ------------------ CONFIGURATION -----------------------
# --------------------------------------------------------
st.set_page_config(page_title="Sales Buddy Chatbot", page_icon="🤖", layout="centered")

# --------------------------------------------------------
# ----------------- SESSION STATE & NAVIGATION -----------
# --------------------------------------------------------
# Initialize the page state if it doesn't exist
if "page" not in st.session_state:
    st.session_state.page = "login"

def navigate(page):
    """
    Sets the new page state and clears the resource cache if navigating 
    away from a page that uses sensitive resources (like the DB connection).
    """
    # Check if we are navigating *away* from a page that uses the cached connection
    # and might need a clean start (login/signup)
    if st.session_state.page in ["login", "signup"] and page not in ["login", "signup"]:
        # Clear the st.cache_resource to force re-establishment of DB connection 
        # or secrets fetch on the next page if needed, preventing stale data/credentials.
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
    # Ensure the chatbot page is rendered without any navigation sidebar (typical for main content)
    chatbot.render(navigate)
