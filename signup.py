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

SECRET_ARN = "arn:aws:secretsmanager:ap-south-1:034362058776:secret:salesbuddy/secrets-0xh2TS"

def get_db_secrets():
    """Fetch DB credentials from AWS Secrets Manager using your actual key names."""
    try:
        client = boto3.client("secretsmanager", region_name="ap-south-1")
        resp = client.get_secret_value(SecretId=SECRET_ARN)
        raw = json.loads(resp["SecretString"])

        # Your secret JSON looks like this:
        # {
        #   "host": "",
        #   "username": "",
        #   "password": "",
        #   "dbname": ""
        # }

        creds = {
            "DB_HOST": raw["host"],
            "DB_USER": raw["username"],
            "DB_PASSWORD": raw["password"],
            "DB_NAME": raw["dbname"]
        }

        return creds

    except Exception as e:
        raise RuntimeError(f"Failed to load DB secrets: {e}")


# --------------------------------------------------------
# ------------------ MYSQL CONNECTION ---------------------
# --------------------------------------------------------

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
        raise RuntimeError(f"MySQL Connection Error: {e}")


# --------------------------------------------------------
# ------------------ SIGNUP PAGE --------------------------
# --------------------------------------------------------

def render(navigate):

    st.markdown("<div class='signup-box'>", unsafe_allow_html=True)

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
                conn = get_conn()
                cur = conn.cursor()

                query = """
                    INSERT INTO users(full_name, email, company, mobile, password)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cur.execute(query, (full_name, email, company, mobile, password))
                conn.commit()
                conn.close()

                st.success("Account Created Successfully! Redirecting...")
                navigate("login")

            except mysql.connector.Error as err:
                st.error(f"Database Error: {err}")
            except Exception as e:
                st.error(f"Unexpected Error: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
