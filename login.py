import streamlit as st
from PIL import Image
import requests
from io import BytesIO


LOGO_URL = "https://raw.githubusercontent.com/ZODOPT-Tech/Wheelbrand/main/images/zodopt.png"

# Define the primary color used for the heading and buttons
PRIMARY_COLOR = "#0B2A63"


def apply_styles():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Inter', sans-serif;
        background-color: #F6F8FB;
        color: #1A1F36;
    }}

    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
    }}

    .left-panel {{
        text-align: center;
        /* Increased padding top to vertically align better */
        padding-top: 100px;
    }}

    .details {{
        margin-top: 35px;
        font-size: 16px;
        font-weight: 500;
        line-height: 2.2;
    }}

    .title {{
        font-size: 32px;
        font-weight: 800;
        margin-bottom: 28px;
        margin-top: 60px;
        color: {PRIMARY_COLOR}; /* Use primary color for title */
    }}

    /* Labels - Ensuring they are visible and styled */
    label {{
        font-size: 15px !important;
        font-weight: 600 !important;
        margin-bottom: 6px !important;
        color: #1A1F36 !important;
    }}
    
    /* Input fields */
    .stTextInput > div > div > input {{
        border-radius: 8px;
        height: 46px;
        background: white;
        font-size: 15px;
        border: 1px solid #CBD5E0;
    }}

    /* Primary Login Button */
    /* Remove the default Streamlit button style to apply custom full-width style */
    div.stButton > button {{
        width: 100%; /* Make the button full width */
        height: 48px;
        border: none;
        border-radius: 8px;
        font-size: 17px;
        font-weight: 700;
        background: {PRIMARY_COLOR}; /* Use primary color */
        color: white;
        margin-top: 20px; /* Add some space above the login button */
    }}

    /* Secondary Buttons (Forgot Password and Create Account) */
    .secondary-container {{
        display: flex;
        gap: 20px;
        justify-content: space-between; /* Adjusted to spread them out */
        margin-top: 20px;
        /* Ensure buttons inside the columns take up the defined secondary button style */
    }}

    /* Style for buttons inside secondary-container columns */
    .secondary-container div.stButton button {{
        width: 100%; /* Make secondary buttons fill their column */
        height: 42px;
        border-radius: 8px;
        font-size: 15px;
        font-weight: 600;
        border: none;
        background: {PRIMARY_COLOR}; /* Use primary color for secondary buttons */
        color: white;
    }}

    /* Adjust the styling of the eye icon for password visibility */
    .stTextInput input[type="password"] + div > button {{
        background: none;
        border: none;
        height: 46px;
    }}

    </style>
    """, unsafe_allow_html=True)


def render(navigate):
    st.set_page_config(layout="wide")
    apply_styles()

    left, right = st.columns([1, 1])

    # Left Side
    with left:
        st.markdown("<div class='left-panel'>", unsafe_allow_html=True)
        try:
            # Attempt to load the logo
            response = requests.get(LOGO_URL)
            response.raise_for_status() # Check for bad status codes
            logo = Image.open(BytesIO(response.content))
            st.image(logo, width=330)
        except Exception as e:
            st.warning(f"Logo Load Error: {e}")

        st.markdown("""
        <div class="details">
        📞 Phone: +123-456-7890 <br>
        ✉️ Email: hello@vclarifi.com <br>
        🌐 Website: www.vclarifi.com <br>
        📍 India
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Right Side
    with right:
        st.markdown("<div class='title'>LOGIN TO YOUR ACCOUNT</div>", unsafe_allow_html=True)

        # Labels are now visible by default with label_visibility="visible"
        # and explicitly named "Email Address" and "Password"
        email = st.text_input("Email Address", label_visibility="visible")
        password = st.text_input("Password", type="password", label_visibility="visible")

        # Primary login button - full width
        # The CSS ensures the st.button here is full-width and styled with the primary color
        if st.button("Login"):
            # Placeholder for login logic
            st.info("Attempting to log in...")
            # navigate("Dashboard") # Uncomment when using a multi-page app structure

        # Secondary buttons side by side
        # Use columns to position buttons side-by-side. The custom CSS will style them.
        st.markdown("<div class='secondary-container'>", unsafe_allow_html=True)

        # Use columns for layout control, each column contains one button
        col_forgot, col_create = st.columns(2)

        with col_forgot:
            if st.button("Forgot Password?", key="forgot_btn"):
                st.info("Navigating to Forgot Password page...")
                # navigate("Forgot") # Uncomment when using a multi-page app structure

        with col_create:
            if st.button("Create Account", key="create_btn"):
                st.info("Navigating to Create Account page...")
                # navigate("Signup") # Uncomment when using a multi-page app structure

        st.markdown("</div>", unsafe_allow_html=True)

# Example to run the render function (optional, based on how you run your Streamlit app)
# if __name__ == "__main__":
#     # Dummy navigate function for testing outside a multi-page app
#     def dummy_navigate(page):
#         st.session_state['current_page'] = page
#         st.experimental_rerun()
#     
#     # Initialize session state if not present (for the dummy navigate function)
#     if 'current_page' not in st.session_state:
#         st.session_state['current_page'] = 'Login'
#         
#     # Simple page routing for testing purposes
#     if st.session_state.get('current_page') == 'Login':
#         render(dummy_navigate)
#     elif st.session_state.get('current_page') == 'Dashboard':
#         st.title("Dashboard")
#         st.button("Go Back to Login", on_click=lambda: dummy_navigate("Login"))
#     elif st.session_state.get('current_page') == 'Forgot':
#         st.title("Forgot Password")
#         st.button("Go Back to Login", on_click=lambda: dummy_navigate("Login"))
#     elif st.session_state.get('current_page') == 'Signup':
#         st.title("Create Account")
#         st.button("Go Back to Login", on_click=lambda: dummy_navigate("Login"))
