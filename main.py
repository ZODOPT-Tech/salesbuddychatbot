import streamlit as st
import login
import signup
import forgot_password
import chatbot  # must contain: def render(navigate, user_data, ACTION_CHIPS)

# --------------------------------------------------------
#                  PAGE CONFIG
# --------------------------------------------------------
st.set_page_config(
    page_title="Sales Buddy Chatbot",
    page_icon="🤖",
    layout="wide"
)

# --------------------------------------------------------
#                 SESSION INITIALIZATION
# --------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "login"

if "reset_email" not in st.session_state:
    st.session_state.reset_email = None

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_data" not in st.session_state:
    st.session_state.user_data = {
        "full_name": "Guest User",
        "email": ""
    }

# Initial AI greeting
if "chat" not in st.session_state:
    st.session_state.chat = [
        {
            "role": "ai",
            "content": "Hello! I have loaded your CRM data. What would you like to know about Acme Corporation?",
            "timestamp": "09:00 AM"
        }
    ]

# Selected CRM lead
if "target_lead" not in st.session_state:
    st.session_state.target_lead = {
        "name": "Acme Corporation",
        "score": "0%",
        "status": "Qualification"
    }

# Sales pipeline steps (chips)
ACTION_CHIPS = [
    "Qualification",
    "Needs Analysis",
    "Proposal/Price Quote",
    "Negotiation/Review",
    "Closed Won"
]

# --------------------------------------------------------
#                   NAVIGATION FUNCTION
# --------------------------------------------------------
def navigate(page):
    """
    Central navigation handler with automatic rerun.
    Clears cached DB connections when leaving login/signup flows.
    """
    if st.session_state.page in ["login", "signup", "forgot_password"] and \
       page not in ["login", "signup", "forgot_password"]:
        st.cache_resource.clear()

    st.session_state.page = page
    st.rerun()


# --------------------------------------------------------
#                  PAGE ROUTER
# --------------------------------------------------------
if st.session_state.page == "login":
    login.render(navigate)

elif st.session_state.page == "signup":
    signup.render(navigate)

elif st.session_state.page == "forgot_password":
    forgot_password.render(navigate)

elif st.session_state.page == "chatbot":

    if not st.session_state.logged_in:
        st.warning("Please log in to access the chatbot.")
        navigate("login")

    # Run ChatGPT-style SalesBuddy
    chatbot.render(
        navigate=navigate,
        user_data=st.session_state.user_data,
        ACTION_CHIPS=ACTION_CHIPS
    )

else:
    st.error("❌ Unknown page request. Redirecting...")
    navigate("login")
