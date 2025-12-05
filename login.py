import streamlit as st
import mysql.connector

# --- Professional CSS Styles ---
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
    box-shadow: 0 8px 25px rgba(0,0,0,0.1); /* Deeper, modern shadow */
    border: 1px solid #eee; /* Subtle border for definition */
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

/* Icon & Input Field Styling */
.input-container {
    margin-bottom: 20px;
}
/* Hides default Streamlit labels for a cleaner look */
.stTextInput > label {
    display: none;
}
/* Style the input fields themselves */
.stTextInput > div > div > input {
    border-radius: 8px;
    border: 1px solid #dcdcdc; /* Lighter, subtle border */
    padding: 12px 15px;
    font-size: 16px;
    color: #333;
}
.stTextInput > div > div > input:focus {
    border-color: #28a745; /* Green focus highlight */
    box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.25);
    outline: none;
}

/* Main Log In Button */
.stButton>button {
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
.stButton>button:hover {
    background-color: #1e7e34;
}

/* Link/Action Button Styling (Forgot Password & Sign Up) */
.action-link {
    background: none !important;
    border: none !important;
    color: #28a745 !important;
    padding: 0 !important;
    text-decoration: none !important;
    cursor: pointer !important;
    margin-top: 0 !important;
    font-weight: 500;
    transition: color 0.3s;
}
.action-link:hover {
    color: #1e7e34 !important;
    text-decoration: underline !important;
}

/* Signup bottom text alignment */
.signup-text {
    text-align: center;
    color: #666;
    margin-top: 20px;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# --- MySQL Connection (Use your actual settings) ---
def get_conn():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="yourpwd",
        database="smart_chatbot_db"
    )

# --- Render Function ---
def render(navigate):
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
    st.markdown("<h2 class='center title-header'>Welcome Back</h2>", unsafe_allow_html=True)
    st.markdown("<p class='center subtitle'>Sign in to **SalesBuddy**</p>", unsafe_allow_html=True)
    
    # --- Input Fields ---
    with st.container():
        # Email Input
        st.markdown("**📧 Email**", unsafe_allow_html=True)
        email = st.text_input("Email", placeholder="your.email@company.com", key="email_input")

        # Password Input
        st.markdown("**🔒 Password**", unsafe_allow_html=True)
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="password_input")
    
    # --- Remember Me and Forgot Password Row ---
    col_remember, col_forgot = st.columns([1.5, 1])
    
    with col_remember:
        remember = st.checkbox("Remember me", key="remember_checkbox", value=True) # Pre-checked for professional look
        
    with col_forgot:
        # Custom button styled as a link, aligned right
        st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
        # Use st.markdown to create a clickable link/button with action-link style
        if st.button("Forgot password?", key="forgot_password_btn", help="Click to reset your password", disabled=False):
            navigate("forgot_password")
        st.markdown("</div>", unsafe_allow_html=True)
        # We need a hack here to apply the style to the Streamlit button element
        st.markdown("""
            <script>
            var buttons = window.parent.document.querySelectorAll('[data-testid="stButton"] button');
            buttons.forEach(function(button) {
                if(button.innerText.includes('Forgot password')) {
                    button.classList.add('action-link');
                }
            });
            </script>
        """, unsafe_allow_html=True)

    # --- Log In Button ---
    if st.button("Log In", use_container_width=True, key="login_button_main"):
        try:
            conn = get_conn()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cur.fetchone()

            if user and user["password"] == password: # Replace with secure hash check in production
                st.success("Login Success! Redirecting...")
                navigate("chatbot")
            else:
                st.error("Incorrect Email or Password")

            conn.close()
        except mysql.connector.Error as err:
            st.error(f"Database error: {err}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

    # --- Sign Up Link ---
    st.markdown("<div class='signup-text'>Don't have an account? ", unsafe_allow_html=True)
    if st.button("Sign up", key="signup_btn", help="Create a new SalesBuddy account"):
        navigate("signup")
    st.markdown("</div>", unsafe_allow_html=True)

    # Hack to style the Sign Up button
    st.markdown("""
        <script>
        var buttons = window.parent.document.querySelectorAll('[data-testid="stButton"] button');
        buttons.forEach(function(button) {
            if(button.innerText.includes('Sign up')) {
                button.classList.add('action-link');
            }
        });
        </script>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    
    # URL navigation override (kept for robustness)
    params = st.query_params
    if "su" in params:
        navigate("signup")
    if "fp" in params:
        navigate("forgot_password")
