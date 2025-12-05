import streamlit as st
import mysql.connector

# --------------------------------------------------------
# -------------------- PROFESSIONAL CSS -------------------
# --------------------------------------------------------
CSS = """
<style>

body {
    background-color: #f5f7fa;
}

/* LOGIN CARD */
.login-card {
    background: #ffffff;
    width: 420px;
    padding: 40px;
    margin: auto;
    margin-top: 60px;
    border-radius: 18px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.08);
    border: 1px solid #e6e6e6;
}

/* HEADER */
.title-header {
    font-size: 30px;
    font-weight: 700;
    color: #222;
    margin-bottom: 5px;
}

.subtitle {
    font-size: 16px;
    color: #666;
    margin-bottom: 25px;
}

/* TEXT INPUTS */
.stTextInput > label {
    display: none;
}

.stTextInput input {
    border-radius: 10px !important;
    border: 1px solid #cccccc !important;
    padding: 12px 14px !important;
    font-size: 16px !important;
}

.stTextInput input:focus {
    border-color: #28a745 !important;
    box-shadow: 0px 0px 0px 2px rgba(40, 167, 69, 0.25) !important;
}

/* PRIMARY LOGIN BUTTON (Ensuring full width) */
div[data-testid="stForm"] > div > div:nth-child(4) > div > div > button { 
    background-color: #28a745 !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 12px !important;
    border: none !important;
    font-size: 18px !important;
    font-weight: 600 !important;
    transition: background-color 0.3s ease;
    width: 100%;
}

div[data-testid="stForm"] > div > div:nth-child(4) > div > div > button:hover {
    background-color: #1f7a38 !important;
}

/* LINK BUTTON STYLE (for Forgot Password & Sign Up) */
/* Targets buttons created in the bottom columns for link styling */
.action-link-button {
    background-color: #28a745 !important; /* Green background */
    color: white !important; /* White text */
    border: none !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    padding: 10px 0 !important;
    margin: 0 !important;
    font-size: 15px !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    width: 100% !important; /* Forces equal width within the column */
}

.action-link-button:hover {
    background-color: #1f7a38 !important; /* Darker green hover */
    text-decoration: none !important;
}

/* Bottom links container adjustment */
.bottom-links {
    margin-top: 25px;
    display: flex;
    justify-content: space-between;
    gap: 10px; /* Space between the two buttons */
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# --------------------------------------------------------
# ------------------ MYSQL CONNECTION ---------------------
# --------------------------------------------------------
def get_conn():
    # NOTE: Replace with your actual connection details
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="yourpwd",
        database="smart_chatbot_db"
    )


# --------------------------------------------------------
# ------------------ LOGIN RENDER FUNCTION ----------------
# --------------------------------------------------------
def render(navigate):
    # Use st.form to group components and handle input submission cleanly,
    # which often helps with the multi-click issue for the primary button.
    with st.container():
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)

        # ---------------- HEADER ----------------
        st.markdown("""
            <div style='text-align:center;'>
                <img src="https://cdn-icons-png.flaticon.com/512/149/149071.png"
                width="70"
                style="background-color:#28a745; border-radius:50%; padding:10px;">
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<h2 class='title-header' style='text-align:center;'>Welcome to Sales Buddy</h2>", unsafe_allow_html=True)
        st.markdown("<p class='subtitle' style='text-align:center;'>Access your account</p>", unsafe_allow_html=True)

        # Use st.form for the login logic
        with st.form(key='login_form'):
            # ---------------- INPUT FIELDS ----------------
            email = st.text_input("Email", placeholder="your.email@company.com", key="email_login")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="password_login")

            # ---------------- REMEMBER ME ----------------
            st.checkbox("Remember me", value=True, key="remember_me")
            
            # ---------------- LOGIN BUTTON ----------------
            submitted = st.form_submit_button("Log In", use_container_width=True, key="login_button_submit")

            if submitted:
                try:
                    conn = get_conn()
                    cur = conn.cursor(dictionary=True)

                    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
                    user = cur.fetchone()

                    if user and user["password"] == password:
                        st.success("Login successful! Redirecting...")
                        navigate("chatbot")
                    else:
                        st.error("Incorrect email or password")

                    conn.close()

                except Exception as e:
                    st.error(f"Error: {e}")

        # ---------------- FORGOT + SIGNUP (SAME LINE, SAME WIDTH, GREEN BUTTONS) ----------------
        st.markdown("<div class='bottom-links'>", unsafe_allow_html=True)
        
        # Use two equal columns (1, 1) to force same width
        col_fp, col_su = st.columns(2)
        
        with col_fp:
            # Forgot Password Button (Green, full width of column)
            if st.button("Forgot Password?", key="fp-btn-stable"):
                navigate("forgot_password")
            
        with col_su:
            # Sign Up Button (Green, full width of column)
            if st.button("Sign Up", key="su-btn-stable"):
                navigate("signup")
                
        st.markdown("</div>", unsafe_allow_html=True)
        
        # --- CSS Styling Application Hack ---
        # Apply the 'action-link-button' style to the two buttons placed in the bottom-links container
        st.markdown("""
            <script>
            var buttons = window.parent.document.querySelectorAll('div[data-testid="stButton"] button');
            buttons.forEach(function(button) {
                var text = button.innerText.trim();
                // Check for exact button text to apply link styling
                if (text === 'Forgot Password?' || text === 'Sign Up') {
                    button.classList.add('action-link-button');
                }
            });
            </script>
        """, unsafe_allow_html=True)


        st.markdown("</div>", unsafe_allow_html=True)
