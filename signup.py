import streamlit as st
import mysql.connector
import boto3
import json

# --------------------------------------------------------
# -------------------- CSS (Green Theme) ------------------
# --------------------------------------------------------
CSS = """
<style>
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
.stButton>button {
    background-color: #28a745 !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 12px !important;
    border: none !important;
    font-size: 18px !important;
    font-weight: 600 !important;
    transition: background-color 0.3s ease;
    margin-top: 20px;
}
.stButton>button:hover {
    background-color: #1f7a38 !important;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# --------------------------------------------------------
# ---------------- AWS Secrets Manager --------------------
# --------------------------------------------------------

# NOTE: Using a static ARN as provided in the original code.
SECRET_ARN = "arn:aws:secretsmanager:ap-south-1:034362058776:secret:salesbuddy/secrets-0xh2TS"

def get_db_secrets():
    """
    Fetch DB credentials from AWS Secrets Manager.
    
    CORRECTED: Uses the exact uppercase keys (DB_HOST, DB_USER, etc.) 
    as configured in the AWS Secret value.
    """
    try:
        # Initialize Boto3 client
        client = boto3.client("secretsmanager", region_name="ap-south-1")
        resp = client.get_secret_value(SecretId=SECRET_ARN)
        
        # Parse the SecretString into a dictionary
        raw = json.loads(resp["SecretString"])

        # Map the exact keys from AWS Secret (uppercase)
        creds = {
            "DB_HOST": raw["DB_HOST"],
            "DB_USER": raw["DB_USER"],
            "DB_PASSWORD": raw["DB_PASSWORD"],
            "DB_NAME": raw["DB_NAME"]
        }

        return creds

    except KeyError as e:
        # Handle the specific case where an expected key is missing
        raise RuntimeError(f"Failed to load DB secrets: Key '{e.args[0]}' not found in AWS Secret. Please check your AWS secret key names (expected: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME).")
    except Exception as e:
        # Handle other AWS/connection exceptions
        raise RuntimeError(f"Failed to load DB secrets: {e}")


# --------------------------------------------------------
# ------------------ MYSQL CONNECTION ---------------------
# --------------------------------------------------------

# Use st.cache_resource for Streamlit to efficiently manage the connection
@st.cache_resource
def get_conn():
    """Connect using AWS secrets (mapped correctly)."""
    creds = get_db_secrets()

    try:
        conn = mysql.connector.connect(
            host=creds["DB_HOST"],
            user=creds["DB_USER"],
            password=creds["DB_PASSWORD"],
            database=creds["DB_NAME"],
            charset="utf8mb4"
        )
        return conn

    except mysql.connector.Error as e:
        # Display an error if the connection fails
        st.error(f"MySQL Connection Error: Could not connect to the database. Details: {e}")
        st.stop()
    except RuntimeError as e:
        # Display an error if secrets fetching fails
        st.error(f"Configuration Error: {e}")
        st.stop()


# --------------------------------------------------------
# ------------------ SIGNUP PAGE --------------------------
# --------------------------------------------------------

def render(navigate):
    """
    Renders the signup form and handles user registration logic.
    
    NOTE: The 'navigate' function must be defined in your main app structure 
    (e.g., using st.session_state for navigation).
    """

    st.markdown("<div class='signup-box'>", unsafe_allow_html=True)

    # Header and image
    st.markdown("""
        <div style='text-align:center;'>
            <img src="https://cdn-icons-png.flaticon.com/512/149/149071.png"
            width="70"
            style="background-color:#28a745; border-radius:50%; padding:10px;">
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<h2 class='title-header center'>Create Your Account</h2>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle center'>Join Sales Buddy today</p>", unsafe_allow_html=True)

    # Input fields 
    full_name = st.text_input("Full Name", placeholder="Full Name")
    email = st.text_input("Email", placeholder="Email Address")
    company = st.text_input("Company", placeholder="Company Name")
    mobile = st.text_input("Mobile", placeholder="Mobile Number")
    password = st.text_input("Password", type="password", placeholder="Password")
    confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm Password")

    if st.button("Sign Up", use_container_width=True):

        if not all([full_name, email, company, mobile, password, confirm_password]):
            st.error("All fields are required")
        elif password != confirm_password:
            st.error("Passwords do not match!")
        else:
            try:
                # Get cached connection
                conn = get_conn()
                cur = conn.cursor()

                query = """
                    INSERT INTO users(full_name, email, company, mobile, password)
                    VALUES (%s, %s, %s, %s, %s)
                """
                # Note: In a real application, you should hash the password 
                # (e.g., using bcrypt) before storing it in the database!
                cur.execute(query, (full_name, email, company, mobile, password))
                conn.commit()
                cur.close()

                st.success("Account Created Successfully! Redirecting...")
                # Assuming 'navigate' is a function passed to switch pages
                if navigate:
                    navigate("login")

            except mysql.connector.Error as err:
                st.error(f"Database Error: {err}")
            except Exception as e:
                st.error(f"Unexpected Error during signup: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------------
# ------------------ APP EXECUTION EXAMPLE ----------------
# --------------------------------------------------------

# Since the original code was a module for a multi-page app (indicated by 'render(navigate)'), 
# we need a simple way to run it if it were the main script.

if __name__ == "__main__":
    # Set page layout to center the content
    st.set_page_config(layout="centered")
    
    # Placeholder for the navigation function, since this file doesn't define the full app structure
    def placeholder_navigate(page):
        st.info(f"Navigation triggered: Should go to the '{page}' page now.")

    render(placeholder_navigate)
