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


# ================== CSS (ChatGPT-Style) =====================
CSS = """
<style>

body, html, .stApp {
    background: #ffffff !important;
    font-family: Inter;
}

/* Remove padding */
.block-container {
    padding-top: 0 !important;
    max-width: 900px !important;
    margin: 0 auto !important;
}

/* Header like ChatGPT */
.top-header {
    position: fixed;
    top: 0;
    left: 0; right: 0;
    background: #ffffff;
    border-bottom: 1px solid #e6e6e6;
    padding: 16px 28px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 999;
}

.top-title {
    font-size: 22px;
    font-weight: 700;
}

.brand-logo {
    font-size: 22px;
    font-weight: 800;
}
.brand-logo span:nth-child(1) { color: #ff3c0a; }
.brand-logo span:nth-child(2) { color: #00c48c; }

/* PAGE WRAPPER */
.page {
    padding-top: 90px;
    padding-bottom: 120px;
}

/* Chat bubble layout */
.chat-wrapper {
    max-width: 780px;
    margin: 0 auto;
    padding: 10px 0;
}

.msg-ai, .msg-user {
    padding: 14px 18px;
    border-radius: 14px;
    font-size: 16px;
    line-height: 1.5;
    margin-bottom: 14px;
    width: fit-content;
    max-width: 80%;
}

/* AI bubble (light gray like ChatGPT) */
.msg-ai {
    background: #f7f7f8;
    border: 1px solid #ececec;
    color: #111;
}

/* User bubble (greenish-white like ChatGPT) */
.msg-user {
    background: #dfffe7;
    border: 1px solid #b2f7c6;
    margin-left: auto;
    color: #111;
}

/* Timestamp */
.time {
    font-size: 11px;
    opacity: 0.7;
    margin-top: 4px;
}

/* Input Bar (fixed like ChatGPT) */
.input-bar {
    position: fixed;
    bottom: 0;
    left: 0; right: 0;
    background: white;
    padding: 14px 16px;
    border-top: 1px solid #e6e6e6;
}

.input-inner {
    max-width: 900px;
    margin: auto;
    display: flex;
    gap: 10px;
}

.send-btn {
    background: #16a05c;
    border-radius: 8px;
    color: white;
    padding: 0 18px;
    font-size: 16px;
    cursor: pointer;
    height: 46px;
    display: flex;
    align-items: center;
}

input[type=text] {
    height: 46px;
    border-radius: 8px;
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


# ================== MAIN CHAT SCREEN =====================
def render(navigate, user_data, ACTION_CHIPS):

    st.markdown(CSS, unsafe_allow_html=True)

    api_key = get_secret()
    df = load_data()
    credits = get_remaining_api_credits()

    if "chat" not in st.session_state:
        st.session_state.chat = []

    if "lead" not in st.session_state:
        st.session_state.lead = {
            "name": "Acme Corporation",
            "score": "0%",
            "status": "Qualification"
        }

    lead = st.session_state.lead


    # ================= HEADER =================
    st.markdown("""
    <div class="top-header">
        <div class="top-title">SalesBuddy Assistant</div>
        <div class="brand-logo"><span>zod</span><span>opt</span></div>
    </div>
    """, unsafe_allow_html=True)


    # ================= PAGE WRAPPER =================
    st.markdown("<div class='page'>", unsafe_allow_html=True)


    # ================= LEAD SUMMARY (ChatGPT-style minimal) =================
    st.markdown(f"""
    <div style="margin-bottom:22px; padding: 10px 4px;">
        <div style="font-size:14px; color:#777;">Lead:</div>
        <div style="font-size:18px; font-weight:700;">{lead['name']}</div>
        <div style="font-size:13px; color:#999;">Status: {lead['status']}</div>
        <div style="font-size:13px; color:#999;">Score: {lead['score']}</div>
    </div>
    """, unsafe_allow_html=True)


    # ================= CHAT AREA =================
    st.markdown("<div class='chat-wrapper'>", unsafe_allow_html=True)

    for msg in st.session_state.chat:
        bubble_class = "msg-user" if msg["role"] == "user" else "msg-ai"
        st.markdown(
            f"<div class='{bubble_class}'>{msg['content']}<div class='time'>{msg['timestamp']}</div></div>",
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)


    # ================= INPUT BAR =================
    st.markdown("<div class='input-bar'><div class='input-inner'>", unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        text = st.text_input("", placeholder="Message SalesBuddy...", key="input_msg")
        send = st.form_submit_button("Send")

        if send and text:
            st.session_state.chat.append({
                "role": "user",
                "content": text,
                "timestamp": time.strftime("%I:%M %p")
            })

    st.markdown("</div></div>", unsafe_allow_html=True)
