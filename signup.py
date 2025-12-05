import streamlit as st
import mysql.connector

# --------------------------------------------------------
# -------------------- PROFESSIONAL CSS -------------------
# --------------------------------------------------------
CSS = """
<style>
/* Style adjustments for professional look and green theme */
.signup-box {
    background: #ffffff;
    width: 420px;
    padding: 40px;
    margin: auto;
    margin-top: 50px;
    border-radius: 18px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.08);
    border: 1px solid #e6e6e6;
}
.center { text-align:center; }
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

/* Hide default labels */
.stTextInput > label {
    display: none;
}

/* Input styling */
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

/* Sign Up Button (Green) */
.stButton>button {
    background-color: #28a745 !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 12px !important;
    border: none !important;
    font-size: 18px !important;
    font-weight: 600 !important;
    transition: background-color 0.3s ease;
    margin-top: 20px; /* Add space above button */
}

.stButton>button:hover {
    background-color: #1f7a38 !important;
}

</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# --------------------------------------------------------
# ------------------ MYSQL CONNECTION ---------------------
# --------------------------------------------------------
# NOTE: The database structure must be updated to include a 'company' column.
def get_conn():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="yourpwd",
        database="smart_chatbot_db"
    )


# --------------------------------------------------------
# ------------------ SIGN UP RENDER FUNCTION ----------------
# --------------------------------------------------------
def render(navigate):
    st.markdown("<div class='signup-box'>", unsafe_allow_html=True)

    # ---------------- HEADER ----------------
    st.markdown("""
        <div style='text-align:center;'>
            <img src="https://cdn-icons-png.flaticon.com/512/149/149071.png"
            width="70"
            style="background-color:#28a745; border-radius:50%; padding:10px;">
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<h2 class='title-header center'>Create Your Account</h2>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle center'>Join Sales Buddy today</p>", unsafe_allow_html=True)

    # ---------------- INPUT FIELDS ----------------
    full_name = st.text_input("Full Name", placeholder="Full Name")
    email = st.text_input("Email", placeholder="Email Address")
    
    # --- ADDED: Company Field ---
    company = st.text_input("Company", placeholder="Company Name")
    
    mobile = st.text_input("Mobile Number", placeholder="Mobile Number")
    
    # --- ADDED: Confirm Password Field ---
    password = st.text_input("Password", type="password", placeholder="Password")
    confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm Password")

    # ---------------- SIGN UP LOGIC ----------------
    if st.button("Sign Up", use_container_width=True):

        # 1. Validation Checks
        if not (full_name and email and company and mobile and password and confirm_password):
            st.error("All fields are required")
        elif password != confirm_password:
            st.error("Passwords do not match!")
        else:
            try:
                conn = get_conn()
                cur = conn.cursor()

                # NOTE: The SQL INSERT statement MUST be updated to include the new 'company' field.
                # Assuming your 'users' table has columns: full_name, email, company, mobile, password
                insert_query = """
                INSERT INTO users(full_name, email, company, mobile, password)
                VALUES (%s, %s, %s, %s, %s)
                """
                cur.execute(insert_query, (full_name, email, company, mobile, password))
                conn.commit()
                conn.close()

                st.success("Account Created Successfully! Redirecting to login...")
                # Redirect to login page on success
                navigate("login")

            except mysql.connector.Error as err:
                st.error(f"Database Error: Could not create account. Check if the 'company' column exists in the 'users' table. Details: {err}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# Note: The 'navigate' function is assumed to be defined and manage the page routing in the main app.
