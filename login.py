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

/* Icon & Input Field Styling */
.stTextInput > label {
    /* Hides default Streamlit labels (like 'Email' and 'Password') */
    display: none;
}
/* Style the input fields themselves */
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

/* Main Log In Button */
.stButton>button {
    background-color: #28a745; /* Green */
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
    background-color: #1e7e34; /* Darker Green */
}

/* Link/Action Button Styling (Forgot Password & Sign Up) */
/* This ensures the 'Forgot password?' and 'Sign up' buttons are green text links */
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
    height: auto !important;
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
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 5px;
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
    # Changed header text as requested
    st.markdown("<h2 class='center title-header'>Welcome to SalesBuddy</h2>", unsafe_allow_html=True)
    st.markdown("<p class='center subtitle'>Sign in to your account</p>", unsafe_allow_html=True)
    
    # --- Input Fields ---
    with st.container():
        # Email Input (No icon/title above the field)
        email = st.text_input("Email", placeholder="your.email@company.com", key="email_input")

        # Password Input (No icon/title above the field)
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="password_input")
    
    # --- Remember Me and Forgot Password Row ---
    col_remember, col_forgot = st.columns([1.5, 1])
    
    with col_remember:
        remember = st.checkbox("Remember me", key="remember_checkbox", value=True)
        
    with col_forgot:
        # Forgot Password link/button
        st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
        if st.button("Forgot password?", key="forgot_password_btn", help="Click to reset your password", disabled=False):
            navigate("forgot_password")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Log In Button ---
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

    # --- Sign Up Link ---
    # Centered alignment for "Don't have an account? Sign up"
    st.markdown("<div class='signup-text'>Don't have an account?", unsafe_allow_html=True)
    if st.button("Sign up", key="signup_btn", help="Create a new SalesBuddy account"):
        navigate("signup")
    st.markdown("</div>", unsafe_allow_html=True)

    # --- CSS Styling Application Hack ---
    # Apply the 'action-link' style to the Forgot Password and Sign Up buttons
    st.markdown("""
        <script>
        var buttons = window.parent.document.querySelectorAll('[data-testid="stButton"] button');
        buttons.forEach(function(button) {
            var text = button.innerText.trim();
            if(text === 'Forgot password?' || text === 'Sign up') {
                button.classList.add('action-link');
            }
        });
        </script>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    
    # URL navigation override
    params = st.query_params
    if "su" in params:
        navigate("signup")
    if "fp" in params:
        navigate("forgot_password")
