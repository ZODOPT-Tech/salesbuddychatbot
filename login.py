import streamlit as st
import mysql.connector
import bcrypt
import os
import base64


# ---------------- UI Helpers ---------------------
def encode_image(image_path):
    if not os.path.exists(image_path):
        return ""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""


def set_background(image_path, default_color_hex="#438454"):
    """Apply global dashboard CSS + fullscreen fix + login layout CSS"""
    bg_style = ""
    if image_path and os.path.exists(image_path):
        encoded_image = encode_image(image_path)
        if encoded_image:
            lower = image_path.lower()
            mime = "image/jpeg" if lower.endswith(("jpg", "jpeg")) else "image/png"
            bg_style = f"""
                background-image: url('data:{mime};base64,{encoded_image}');
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
            """
        else:
            bg_style = f"background-color: {default_color_hex};"
    else:
        bg_style = f"background-color: {default_color_hex};"

    st.markdown(
        f"""
    <style>
    /* ===========================
       GLOBAL BACKGROUND
    ============================ */
    [data-testid="stAppViewContainer"] {{
        {bg_style}
        background-attachment: fixed;
    }}

    /* Remove gaps */
    .block-container {{
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }}

    .stApp > header, .stApp > footer {{
        display:none !important;
    }}

    html, body {{
        overflow:hidden !important;
        padding:0 !important;
        margin:0 !important;
        height:100vh !important;
        width:100vw !important;
    }}

    /* ===========================
       FULLSCREEN LOGIN CONTAINER
    ============================ */
    .fullscreen-login-container {{
        display: flex;
        flex-direction: row;
        width:100vw;
        height:100vh;
        overflow:hidden;
    }}

    .login-left {{
        flex: 1;
        padding: 7vh 6vw;
        color:white;
        display:flex;
        flex-direction:column;
        justify-content:center;
    }}

    .login-title {{
        font-size:64px;
        font-weight:800;
        line-height:1.1;
        margin-bottom:12px;
    }}

    .login-sub {{
        font-size:22px;
        margin-bottom:50px;
    }}

    .login-form-card {{
        width:460px;
        background:rgba(0,0,0,0.65);
        backdrop-filter:blur(8px);
        border-radius:20px;
        padding:40px 32px;
        box-shadow:0px 6px 20px rgba(0,0,0,0.35);
    }}

    .login-right {{
        flex:1;
        padding:7vh 6vw;
        display:flex;
        flex-direction:column;
        justify-content:center;
        color:white;
        background:rgba(0,0,0,0.35);
        backdrop-filter:blur(6px);
        border-left:1px solid rgba(255,255,255,0.2);
    }}

    .right-title {{
        font-size:62px;
        font-weight:800;
        margin-bottom:18px;
        line-height:1.15;
    }}

    .right-desc {{
        font-size:22px;
        max-width:350px;
        margin-bottom:60px;
    }}

    /* Inputs */
    .stTextInput > div > div > input {{
        background:#1a1a1a !important;
        border:1px solid #555 !important;
        color:white !important;
        border-radius:14px !important;
        padding:16px !important;
        font-size:18px;
    }}

    /* Button */
    form button {{
        background:#00b894 !important;
        color:white !important;
        font-weight:700 !important;
        border:none !important;
        border-radius:14px !important;
        padding:16px !important;
        font-size:20px !important;
        margin-top:20px;
        width:100%;
    }}

    .stButton>button {{
        background:white !important;
        color:black !important;
        font-weight:700 !important;
        padding:14px 30px !important;
        font-size:18px !important;
        border-radius:14px !important;
        border:none !important;
        width:max-content;
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )


# ------------------ DB -----------------------
def get_db():
    return mysql.connector.connect(
        host="localhost", user="root", password="", database="salesbuddy"
    )


# ------------------- UI ----------------------
def render(navigate):
    set_background("images/bg.jpg")

    st.markdown("<div class='fullscreen-login-container'>", unsafe_allow_html=True)

    # LEFT
    st.markdown("<div class='login-left'>", unsafe_allow_html=True)
    st.markdown("<div class='login-title'>Login to Your<br>Account</div>", unsafe_allow_html=True)
    st.markdown("<div class='login-sub'>Access your account</div>", unsafe_allow_html=True)

    st.markdown("<div class='login-form-card'>", unsafe_allow_html=True)
    with st.form("login"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        ok = st.form_submit_button("Sign In")

        if ok:
            try:
                conn = get_db()
                cur = conn.cursor(dictionary=True)
                cur.execute("SELECT * FROM users WHERE email=%s", (email,))
                user = cur.fetchone()
                cur.close()
                if user and bcrypt.checkpw(password.encode(), user["password"].encode()):
                    st.session_state.logged_in = True
                    st.session_state.user_data = user
                    navigate("dashboard")
                else:
                    st.error("Invalid login")
            except Exception as e:
                st.error("Login failed")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # RIGHT
    st.markdown("<div class='login-right'>", unsafe_allow_html=True)
    st.markdown("<div class='right-title'>New Here?</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='right-desc'>Sign up and discover a great amount of new opportunities!</div>",
        unsafe_allow_html=True,
    )

    if st.button("Sign Up"):
        navigate("signup")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ---------- Local test --------------
if __name__ == "__main__":
    def go(x):
        st.success(f"Navigate → {x}")
    render(go)
