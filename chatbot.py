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


# ================== CSS =====================
CSS = """
<style>
html, body, .stApp {
    margin:0 !important;
    padding:0 !important;
    background:#f7f8fa;
}

/* Main container full width */
.block-container {
    padding:0 !important;
    margin:0 auto !important;
    max-width:900px !important;
}

/* --- Lead Section --- */
.lead-card {
    background:white;
    padding:26px;
    border-radius:16px;
    margin-top:20px;
    box-shadow:0 3px 14px rgba(0,0,0,0.06);
}
.lead-title {
    font-size:20px;
    font-weight:700;
    margin-bottom:4px;
}
.lead-sub {
    font-size:14px;
    color:#777;
}

/* --- Chat Messages --- */
.chat-container {
    padding:20px 2px 120px 2px;
}

.msg-user {
    background:#16a05c;
    color:white;
    padding:12px 18px;
    border-radius:18px 18px 0 18px;
    max-width:65%;
    margin-left:auto;
    margin-bottom:16px;
}
.msg-ai {
    background:white;
    padding:12px 18px;
    border-radius:18px 18px 18px 0;
    border:1px solid #eee;
    max-width:65%;
    margin-bottom:16px;
}
.time {
    font-size:11px;
    opacity:0.7;
    margin-top:4px;
}

/* --- Input Bar --- */
.input-bar {
    position:fixed;
    bottom:0;
    left:0;
    right:0;
    max-width:900px;
    margin:auto;
    background:white;
    padding:14px 10px;
    border-top:1px solid #ddd;
}
.send-btn {
    height:48px;
    width:70px;
    background:#16a05c;
    border-radius:12px;
    font-size:17px;
    color:white;
    font-weight:600;
}

</style>
"""


# ================== HELPERS =====================
def get_remaining_api_credits():
    return random.randint(2500, 5000)


@st.cache_resource
def get_secret():
    try:
        client = boto3.client('secretsmanager', region_name=AWS_REGION)
        val = client.get_secret_value(SecretId=GEMINI_SECRET_NAME)
        return json.loads(val['SecretString'])[GEMINI_SECRET_KEY]
    except:
        return None


@st.cache_data
def load_data():
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=S3_BUCKET_NAME, Key=S3_FILE_KEY)
    df = pd.read_excel(BytesIO(obj['Body'].read()))
    df.columns = df.columns.str.strip()
    return df[REQUIRED_COLS]


def ask_gemini(query, key):
    genai.configure(api_key=key)
    model = genai.GenerativeModel(GEMINI_MODEL)
    r = model.generate_content(query)
    return r.text


# ================== MAIN RENDER =====================
def render(navigate, user_data, ACTION_CHIPS):

    st.markdown(CSS, unsafe_allow_html=True)

    api_key = get_secret()
    df = load_data()
    credits = get_remaining_api_credits()

    # Initialize memory
    if "chat" not in st.session_state:
        st.session_state.chat = []

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "lead" not in st.session_state:
        st.session_state.lead = {
            "name":"Acme Corporation",
            "score":"0%",
            "status":"Qualification"
        }

    lead = st.session_state.lead

    # ---------------------------------------------------------------------
    # ⭐ CHATGPT-STYLE SIDEBAR
    # ---------------------------------------------------------------------
    with st.sidebar:

        # Logo + Heading
        st.markdown("""
            <div style='text-align:center;padding:18px 0;'>
                <img src="https://raw.githubusercontent.com/ZODOPT-Tech/Wheelbrand/main/images/zodopt.png"
                     style="width:70px;margin-bottom:10px;">
                <div style="font-size:22px;font-weight:800;">SalesBuddy</div>
            </div>
            <hr>
        """, unsafe_allow_html=True)

        # New Chat Button
        if st.button("➕  New Chat", use_container_width=True):
            if len(st.session_state.chat) > 0:
                st.session_state.chat_history.append(st.session_state.chat)

            st.session_state.chat = [{
                "role": "ai",
                "content": "Hello! I have loaded your CRM data. What would you like to know?",
                "timestamp": time.strftime("%I:%M %p")
            }]
            st.rerun()

        # History List
        st.markdown("### History")
        if len(st.session_state.chat_history) == 0:
            st.caption("No previous chats.")
        else:
            for i, conv in enumerate(st.session_state.chat_history):
                title = conv[0]["content"][:25] + "..." if len(conv[0]["content"]) > 25 else conv[0]["content"]

                if st.button(f"💬 {title}", key=f"hist_{i}", use_container_width=True):
                    st.session_state.chat = conv
                    st.rerun()

    # ---------------------------------------------------------------------
    # MAIN CHAT SCREEN
    # ---------------------------------------------------------------------

    # --- Lead card ---
    st.markdown(f"""
    <div class="lead-card">
        <div class="lead-title">{lead['name']}</div>
        <div class="lead-sub">Status: {lead['status']} • Score: {lead['score']}</div>
    </div>
    """, unsafe_allow_html=True)

    # --- Messages ---
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for msg in st.session_state.chat:
        bubble_class = "msg-user" if msg["role"] == "user" else "msg-ai"
        st.markdown(
            f"""
            <div class='{bubble_class}'>
                {msg['content']}
                <div class='time'>{msg['timestamp']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Input Bar ---
    st.markdown("<div class='input-bar'>", unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([8, 1.2])

        with col1:
            query = st.text_input("", placeholder="Message SalesBuddy...")

        with col2:
            send = st.form_submit_button("Send", use_container_width=True)

        if send and query:
            # Add user message
            st.session_state.chat.append({
                "role": "user",
                "content": query,
                "timestamp": time.strftime("%I:%M %p")
            })

            # Get AI Response
            reply = ask_gemini(query, api_key)

            st.session_state.chat.append({
                "role": "ai",
                "content": reply,
                "timestamp": time.strftime("%I:%M %p")
            })

            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
