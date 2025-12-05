import streamlit as st
import mysql.connector

# CSS included directly - Adjusted for image style (green accents, subtle box shadow)
CSS = """
<style>
/* Streamlit elements styling */
.stTextInput > div > div > input {
    border-radius: 8px;
    border: 1px solid #ccc; /* Lighter border for input fields */
    padding: 10px;
}
.stButton>button {
    background-color: #28a745; /* Green button */
    color: white;
    border-radius: 8px;
    font-weight: bold;
    padding: 10px;
    margin-top: 10px;
    border: none;
    box-shadow: none;
}
.stButton>button:hover {
    background-color: #1e7e34; /* Darker green on hover */
}
/* Custom classes for the login box */
.login-box {
    background: #ffffff;
    width: 420px;
    padding: 40px;
    margin: auto;
    margin-top: 50px;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1); /* Softer shadow */
}
.center { text-align:center; }
.green-text-button {
    background: none !important;
    border: none !important;
    color: #28a745 !important; /* Green text color */
    padding: 0 !important;
    text-decoration: none !important;
    cursor: pointer !important;
    margin-top: 0 !important;
    text-align: right;
    font-weight: 400; /* Regular weight for links/buttons */
    display: inline-block;
}
.green-text-button:hover {
    color: #1e7e34 !important; /* Darker green on hover */
    text-decoration: underline !important;
}
/* Hide default labels for cleaner look */
div[data-testid="stForm"] label {
    display: none;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# MySQL connection (Placeholder: replace with your actual DB credentials)
def get_conn():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="yourpwd",
        database="smart_chatbot_db"
    )

def render(navigate):
    # Use a placeholder for the login box to match the image dimensions
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    
    # Header Section
    col_icon, col_text = st.columns([1, 4])
    with col_icon:
        # User icon image with green background
        st.markdown(
            f"""
            <div class='center' style='margin-bottom: 20px;'>
                <img src="https://cdn-icons-png.flaticon.com/512/149/149071.png" 
                     width=70 
                     style="background-color: #28a745; border-radius: 50%; padding: 10px;">
            </div>
            """, 
            unsafe_allow_html=True
        )

    st.markdown("<h2 class='center'>Welcome Back</h2>", unsafe_allow_html=True)
    st.markdown("<p class='center'>Sign in to **SalesBuddy**</p>", unsafe_allow_html=True)
    
    # ---
    
    # Input Fields (using icon placeholding)
    
    # Email Input
    st.markdown(f"**<span style='color: #444;'>📧 Email</span>**", unsafe_allow_html=True)
    email = st.text_input("Email", placeholder="your.email@company.com", key="email_input")

    # Password Input
    st.markdown(f"**<span style='color: #444;'>🔒 Password</span>**", unsafe_allow_html=True)
    password = st.text_input("Password", type="password", placeholder="Enter your password", key="password_input")
    
    # ---
    
    # Checkbox and Forgot Password Link/Button
    col_remember, col_forgot = st.columns([1.5, 1])
    
    # Remember Me Checkbox
    with col_remember:
        remember = st.checkbox("Remember me", key="remember_checkbox")
        
    # Forgot Password Button (using Streamlit button with custom CSS)
    with col_forgot:
        # Use an empty container to push the button/link to the right
        st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
        # Create a Streamlit button and apply the custom 'green-text-button' style
        if st.button("Forgot password?", key="forgot_password_btn"):
            navigate("forgot_password")
        st.markdown("</div>", unsafe_allow_html=True)


    # ---
    
    # Log In Button
    if st.button("Log In", use_container_width=True, key="login_button_main"):
        try:
            conn = get_conn()
            cur = conn.cursor(dictionary=True)

            cur.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cur.fetchone()

            # Placeholder for actual password check logic (e.g., bcrypt)
            # This example uses plain text for demonstration/simplicity
            if user and user["password"] == password:
                st.success("Login Success!")
                # In a real app, you would set a session state here
                navigate("chatbot")
            else:
                st.error("Incorrect Email or Password")

            conn.close()
        except mysql.connector.Error as err:
            st.error(f"Database error: {err}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

    # ---
    
    # Don't have an account? Sign up section
    st.markdown("<br>", unsafe_allow_html=True)
    col_signup_1, col_signup_2 = st.columns([1.5, 1.5])
    
    with col_signup_1:
        st.markdown("<p style='text-align: right; margin: 0;'>Don't have an account?</p>", unsafe_allow_html=True)

    with col_signup_2:
        # Sign up button (using Streamlit button with custom CSS)
        if st.button("Sign up", key="signup_btn"):
            navigate("signup")
            
    st.markdown("</div>", unsafe_allow_html=True)

    # URL navigation override (kept for full functionality)
    params = st.query_params
    if "su" in params:
        navigate("signup")
    if "fp" in params:
        navigate("forgot_password")

# Note: The `Maps` function is assumed to be defined elsewhere in your main application script.
# If you are running this code alone, you would need to define a simple 'navigate' function:
# def navigate(page):
#     st.session_state.page = page
# st.session_state.page = 'login' # Initial state
# render(navigate)
