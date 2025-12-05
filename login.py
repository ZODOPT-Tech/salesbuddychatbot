import streamlit as st
import mysql.connector

# --- Robust Professional CSS Styles ---
# Simplified CSS focusing on the main box, inputs, and primary button
CSS = """
<style>
/* Global Box Styling */
.login-box {
    background: #ffffff;
    width: 420px;
    padding: 40px;
    margin: auto;
    margin-top: 50px;
    border-radius: 16px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    border: 1px solid #eee;
}
.center { text-align:center; }
.title-header {
    font-size: 28px;
    font-weight: 700;
    color: #333;
    margin-bottom: 5px;
}
.subtitle {
    font-size: 16px;
    color: #666;
    margin-bottom: 30px;
}

/* Input Field Styling */
.stTextInput > label {
    /* Hides default Streamlit labels */
    display: none;
}
.stTextInput > div > div > input {
    border-radius: 8px;
    border: 1px solid #dcdcdc;
    padding: 12px 15px;
    font-size: 16px;
    color: #333;
}
.stTextInput > div > div > input:focus {
    border-color: #28a745;
    box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.25);
    outline: none;
}

/* Main Log In Button - Green */
div.stButton button {
    background-color: #28a745; 
    color: white;
    border-radius: 8px;
    font-weight: 600;
    padding: 12px;
    margin-top: 20px;
    border: none;
    box-shadow: none;
    font-size: 18px;
    transition: background-color 0.3s;
}
div.stButton button:hover {
    background-color: #1e7e34;
}

/* Green Link Styling for "Forgot password?" and "Sign up" */
/* Targets any anchor tag (a) inside the login box that we generate via markdown */
.login-box a {
    color: #28a745 !important;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.3s;
}
.login-box a:hover {
    color: #1e7e34 !important;
    text-decoration: underline;
}

/* Aligning Remember Me and Forgot Password */
div[data-testid="stHorizontalBlock"] {
    align-items: center;
}
div[data-testid="column"] {
    display: flex;
    flex-direction: column;
    justify-content: center;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# --- MySQL Connection (Placeholder) ---
def get_conn():
    # NOTE: Replace with your actual connection details
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="yourpwd",
        database="smart_chatbot_db"
    )

# --- Render Function ---
def render(navigate):
    # Main login container
    with st.container():
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        
        # 1. Header and Icon
        st.markdown(
            f"""
            <div class='center' style='margin-bottom: 25px;'>
                <img src="https://cdn-icons-png.flaticon.com/512/149/149071.png" 
                     width=70 
                     style="background-color: #28a745; border-radius: 50%; padding: 10px;">
            </div>
            """, 
            unsafe_allow_html=True
        )
        st.markdown("<h2 class='center title-header'>Welcome to SalesBuddy</h2>", unsafe_allow_html=True)
        st.markdown("<p class='center subtitle'>Sign in to your account</p>", unsafe_allow_html=True)
        
        # 2. Input Fields
        email = st.text_input("Email", placeholder="your.email@company.com", key="email_input")
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="password_input")
        
        # 3. Remember Me and Forgot Password Row
        col_remember, col_forgot = st.columns([1.5, 1])
        
        with col_remember:
            st.checkbox("Remember me", key="remember_checkbox", value=True)
            
        with col_forgot:
            # Using Markdown link for 'Forgot password?' ensures green text and click functionality
            # Note: navigate() needs to be handled by a Streamlit session state change in a real app,
            # but for a simple link appearance, this Markdown works best.
            forgot_html = "<div style='text-align: right; margin-top: 10px;'>"
            forgot_html += "<a href='#' onclick='window.parent.document.querySelector(\"[data-testid=\\\"stFileUploadDropzone\\\"], [data-testid=\\\"stFileUploader\\\"], [data-testid=\\\"stForm\\\"]).innerHTML = \"<p>Redirecting to Forgot Password...</p>\";'>Forgot password?</a>"
            forgot_html += "</div>"
            st.markdown(forgot_html, unsafe_allow_html=True)

        # 4. Log In Button
        if st.button("Log In", use_container_width=True, key="login_button_main"):
            try:
                conn = get_conn()
                cur = conn.cursor(dictionary=True)
                cur.execute("SELECT * FROM users WHERE email=%s", (email,))
                user = cur.fetchone()

                if user and user["password"] == password: 
                    st.success("Login Success! Redirecting...")
                    navigate("chatbot")
                else:
                    st.error("Incorrect Email or Password")

                conn.close()
            except mysql.connector.Error as err:
                st.error(f"Database error: {err}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

        # 5. Sign Up Section (Forgot Password and Sign Up Next to Next - Now done cleanly)
        st.markdown("<br>", unsafe_allow_html=True)
        col_signup_text, col_signup_link = st.columns([1.5, 1])
        
        with col_signup_text:
            st.markdown("<p style='text-align: right; color: #666; margin-top: 8px;'>Don't have an account?</p>", unsafe_allow_html=True)
        
        with col_signup_link:
            # Using Markdown link for 'Sign up' ensures green text
            signup_html = "<div style='text-align: left; margin-top: 8px;'>"
            signup_html += "<a href='#' onclick='window.parent.document.querySelector(\"[data-testid=\\\"stFileUploadDropzone\\\"], [data-testid=\\\"stFileUploader\\\"], [data-testid=\\\"stForm\\\"]).innerHTML = \"<p>Redirecting to Sign Up...</p>\";'>Sign up</a>"
            signup_html += "</div>"
            st.markdown(signup_html, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        
    # URL navigation override (for actual functionality if running in multi-page app)
    params = st.query_params
    if "su" in params:
        navigate("signup")
    if "fp" in params:
        navigate("forgot_password")
