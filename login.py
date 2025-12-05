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

/* MAIN LOGIN BUTTON */
/* Target the button inside the column for the main login button */
div[data-testid="stHorizontalBlock"] > div:nth-child(1) > div > div > button {
    background-color: #28a745 !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 12px !important;
    border: none !important;
    font-size: 18px !important;
    font-weight: 600 !important;
    transition: background-color 0.3s ease;
    width: 100%; /* Ensure full width */
}

div[data-testid="stHorizontalBlock"] > div:nth-child(1) > div > div > button:hover {
    background-color: #1f7a38 !important;
}

/* LINK BUTTON STYLE (for Forgot Password & Sign Up) */
/* Target buttons in the bottom row with a different style (Link/Text style) */
.action-link-button {
    background: none !important;
    border: none !important;
    color: #28a745 !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    padding: 0 !important;
    margin: 0 !important;
    font-size: 15px !important;
    box-shadow: none !important; /* Remove shadow */
    width: auto !important; /* Allow auto width */
}

.action-link-button:hover {
    text-decoration: underline !important;
    color: #1f7a38 !important;
    background: none !important;
}

/* Bottom row links container */
.bottom-links {
    display: flex;
    justify-content: space-around; /* Distribute links evenly */
    margin-top: 25px;
    align-items: center;
}

/* Ensure consistent button styling for links (Hack for Streamlit buttons) */
div[data-testid="stButton"] button {
    transition: all 0.3s ease; /* Apply transition to all buttons */
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

    st.markdown("<div class='login-card'>", unsafe_allow_html=True)

    # ---------------- HEADER ----------------
    st.markdown("""
        <div style='text-align:center;'>
            <img src="https://cdn-icons-png.flaticon.com/512/149/149071.png"
            width="70"
            style="background-color:#28a745; border-radius:50%; padding:10px;">
        </div>
    """, unsafe_allow_html=True)

    # --- UPDATED HEADER TEXT ---
    st.markdown("<h2 class='title-header' style='text-align:center;'>Welcome to Sales Buddy</h2>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle' style='text-align:center;'>Access your account</p>", unsafe_allow_html=True)

    # ---------------- INPUT FIELDS ----------------
    email = st.text_input("Email", placeholder="your.email@company.com", key="email_login")
    password = st.text_input("Password", type="password", placeholder="Enter your password", key="password_login")

    # ---------------- REMEMBER ME ----------------
    st.checkbox("Remember me", value=True, key="remember_me")

    # ---------------- LOGIN BUTTON (Using a column for better control) ----------------
    col_login_btn, = st.columns([1])
    with col_login_btn:
        if st.button("Log In", use_container_width=True, key="login_button"):
            try:
                conn = get_conn()
                cur = conn.cursor(dictionary=True)

                cur.execute("SELECT * FROM users WHERE email=%s", (email,))
                user = cur.fetchone()

                if user and user["password"] == password:
                    st.success("Login successful! Redirecting...")
                    # --- STABLE NAVIGATION ---
                    navigate("chatbot") 
                else:
                    st.error("Incorrect email or password")

                conn.close()

            except Exception as e:
                st.error(f"Error: {e}")

    # ---------------- FORGOT + SIGNUP (CENTERED, SAME LINE) ----------------
    # Use columns to align the text in the middle and place buttons side-by-side
    st.markdown("<div class='bottom-links'>", unsafe_allow_html=True)

    # Forgot Password Link/Button
    if st.button("Forgot Password?", key="fp-btn-stable"):
        # --- STABLE NAVIGATION ---
        navigate("forgot_password")
        
    # Sign Up Link/Button
    if st.button("Sign Up", key="su-btn-stable"):
        # --- STABLE NAVIGATION ---
        navigate("signup")

    st.markdown("</div>", unsafe_allow_html=True)

    # --- CSS Styling Application Hack (Targets the two new buttons) ---
    # We apply the action-link-button style to the two buttons placed in the bottom-links container
    st.markdown("""
        <script>
        var fpBtn = window.parent.document.querySelector('[data-testid="stButton"] button[kind="secondaryFormSubmit"]:contains("Forgot Password?")');
        var suBtn = window.parent.document.querySelector('[data-testid="stButton"] button[kind="secondaryFormSubmit"]:contains("Sign Up")');
        
        // Find by text content if query selector fails
        var buttons = window.parent.document.querySelectorAll('div[data-testid="stButton"] button');
        buttons.forEach(function(button) {
            var text = button.innerText.trim();
            if (text === 'Forgot Password?' || text === 'Sign Up') {
                button.classList.add('action-link-button');
            }
        });
        </script>
    """, unsafe_allow_html=True)


    st.markdown("</div>", unsafe_allow_html=True)

    # The URL navigation override is no longer needed since the buttons handle navigation directly.
