import streamlit as st
import pandas as pd
import time
import boto3
import json
import random
from io import BytesIO
import google.generativeai as genai


# ================== CONFIG =====================
S3_BUCKET_NAME = "zodopt"
S3_FILE_KEY = "Leaddata/Leads by Status.xlsx"
AWS_REGION = "ap-south-1"
GEMINI_SECRET_NAME = "salesbuddy/secrets"
GEMINI_SECRET_KEY = "GEMINI_API_KEY"
GEMINI_MODEL = "gemini-2.5-flash"

REQUIRED_COLS = [
    "Record Id", "Full Name", "Lead Source", "Company", "Lead Owner",
    "Street", "City", "State", "Country", "Zip Code",
    "First Name", "Last Name", "Annual Revenue", "Lead Status"
]

# ================== UI CSS =====================
CSS = """
<style>

html, body {
    margin:0 !important;
    padding:0 !important;
}
.stApp {
    background:#f8f9fc !important;
}

/* Remove streamlit header, footer, menu */
#MainMenu, header, footer {visibility:hidden;}

.sidebar {
    background:#ffffff !important;
}

.block-container {
    padding:0 !important;
}

/* ===== SIDEBAR ===== */
.sidebar-logo {
    text-align:center;
    padding:25px 0 10px 0;
}
.sidebar-logo img {
    width:80px;
}
.sidebar-title {
    text-align:center;
    font-size:26px;
    font-weight:800;
    margin-bottom:20px;
}

.sidebar-button > button {
    width:100%;
    background:#eee !important;
    color:#222 !important;
    border-radius:10px !important;
    padding:10px !important;
}

/* ===== Chat Container ===== */
.chat-wrapper {
    padding:20px 40px 140px 40px;
}

/* AI message */
.msg-ai {
    background:white;
    padding:14px 20px;
    border-radius:16px 16px 16px 4px;
    max-width:70%;
    border:1px solid #ececec;
    margin-bottom:12px;
}

/* User message */
.msg-user {
    background:#17a365;
    color:white;
    padding:14px 20px;
    border-radius:16px 16px 4px 16px;
    max-width:70%;
    margin-left:auto;
    margin-bottom:12px;
}

.time {
    font-size:11px;
    opacity:0.7;
    margin-top:6px;
}

/* Input Bar */
.input-bar {
    position:fixed;
    bottom:0;
    left:0;
    right:0;
    padding:14px 20px;
    background:white;
    border-top:1px solid #ddd;
}
.input-row {
    display:flex;
    gap:10px;
}
.send-btn {
    background:#17a365 !important;
    color:white !important;
    border-radius:8px !important;
    font-weight:600 !important;
}
</style>
"""


# ================== HELPERS =====================
def get_remaining_api_credits():
    return random.randint(2000, 5000)


@st.cache_resource
def get_secret():
    try:
        client = boto3.client("secretsmanager", region_name=AWS_REGION)
        val = client.get_secret_value(SecretId=GEMINI_SECRET_NAME)
        return json.loads(val["SecretString"])[GEMINI_SECRET_KEY]
    except:
        return None


@st.cache_data
def load_data():
    s3 = boto3.client("s3")
    obj = s3.get_object(Bucket=S3_BUCKET_NAME, Key=S3_FILE_KEY)
    df = pd.read_excel(BytesIO(obj["Body"].read()))
    df.columns = df.columns.str.strip()
    return df[REQUIRED_COLS]


def ask_gemini(query, key):
    genai.configure(api_key=key)
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(query)
    return response.text


# ================== MAIN UI =====================
def render(navigate=None, user_data=None, ACTION_CHIPS=None):

    st.markdown(CSS, unsafe_allow_html=True)

    api_key = get_secret()
    credits = get_remaining_api_credits()
    df = load_data()

    # Init session chat
    if "chat" not in st.session_state:
        st.session_state.chat = [
            {
                "role": "ai",
                "content": "Hello! I have loaded your CRM data. What would you like to know?",
                "timestamp": time.strftime("%I:%M %p")
            }
        ]

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # ================== SIDEBAR =====================
    with st.sidebar:
        st.markdown("""
            <div class='sidebar-logo'>
                <img src="https://raw.githubusercontent.com/ZODOPT-Tech/Wheelbrand/main/images/zodopt.png">
            </div>
            <div class='sidebar-title'>SalesBuddy</div>
            <hr>
        """, unsafe_allow_html=True)

        # New Chat Button
        st.markdown("<div class='sidebar-button'>", unsafe_allow_html=True)
        if st.button("➕  New Chat"):
            # Save previous chat
            if len(st.session_state.chat) > 0:
                st.session_state.chat_history.append(st.session_state.chat)

            # Reset chat
            st.session_state.chat = [
                {
                    "role": "ai",
                    "content": "Hello! How can I assist you today?",
                    "timestamp": time.strftime("%I:%M %p")
                }
            ]
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("### History")
        if len(st.session_state.chat_history) == 0:
            st.caption("No previous chats.")
        else:
            for i, hist in enumerate(st.session_state.chat_history):
                title = hist[0]["content"][:25] + "..."
                if st.button(f"💬 {title}", key=f"hist_{i}"):
                    st.session_state.chat = hist
                    st.rerun()

    # ================== CHAT WINDOW =====================
    st.markdown("<div class='chat-wrapper'>", unsafe_allow_html=True)

    for msg in st.session_state.chat:
        bubble = "msg-user" if msg["role"] == "user" else "msg-ai"
        align_style = "margin-left:auto;" if msg["role"] == "user" else "margin-right:auto;"

        st.markdown(
            f"""
            <div style="{align_style}">
                <div class="{bubble}">
                    {msg['content']}
                    <div class="time">{msg['timestamp']}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # Spacer for bottom input bar
    st.markdown("<div style='height:110px;'></div>", unsafe_allow_html=True)

    # ================== FIXED INPUT BAR =====================
    st.markdown("<div class='input-bar'><div class='input-row'>", unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([8, 1])

        user_input = col1.text_input(
            "",
            placeholder="Message SalesBuddy...",
            label_visibility="collapsed"
        )

        send = col2.form_submit_button("Send")

        if send and user_input:
            # Add user message
            st.session_state.chat.append({
                "role": "user",
                "content": user_input,
                "timestamp": time.strftime("%I:%M %p")
            })

            # AI Reply
            reply = ask_gemini(user_input, api_key) if api_key else "Gemini API key not configured."

            st.session_state.chat.append({
                "role": "ai",
                "content": reply,
                "timestamp": time.strftime("%I:%M %p")
            })

            st.rerun()

    st.markdown("</div></div>", unsafe_allow_html=True)
