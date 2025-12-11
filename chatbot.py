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


# ================== CSS (Fully Clean — No Header) =====================
CSS = """
<style>

/* REMOVE STREAMLIT DEFAULT HEADER COMPLETELY */
header[data-testid="stHeader"] { display: none !important; }
div.block-container { padding-top: 0 !important; }

/* FULL SCREEN CHAT UI */
html, body, .stApp {
    height: 100%;
    margin: 0;
    padding: 0;
    overflow: hidden; /* No browser scroll */
    background: #ffffff;
    font-family: Inter, system-ui;
}

/* Page layout container */
.page {
    position: absolute;
    top: 0;
    bottom: 72px; /* input bar height */
    left: 0; right: 0;
    overflow-y: auto; /* internal chat scroll only */
    padding: 20px;
    display: flex;
    justify-content: center;
}

/* Chat column */
.chat-column {
    width: 780px;
    max-width: calc(100% - 40px);
    display: flex;
    flex-direction: column;
    gap: 12px;
}

/* Lead Summary Card */
.lead-summary {
    background: white;
    border-radius: 12px;
    padding: 16px 20px;
    border: 1px solid #efefef;
    display: flex;
    flex-direction: column;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

/* Hide 3 dots or action icons */
.lead-summary .lead-actions { display: none !important; }

/* Chat Messages */
.msg-ai, .msg-user {
    padding: 14px 18px;
    border-radius: 16px;
    font-size: 16px;
    line-height: 1.5;
    width: fit-content;
    max-width: 85%;
    margin-bottom: 12px;
}

.msg-ai {
    background: #f7f7f8;
    border: 1px solid #ececec;
    color: #111;
}

.msg-user {
    background: #dfffe7;
    border: 1px solid #b2f7c6;
    margin-left: auto;
    color: #111;
}

.time {
    font-size: 11px;
    opacity: 0.6;
    margin-top: 4px;
}

/* Input bar */
.input-bar {
    position: fixed;
    bottom: 0;
    left: 0; right: 0;
    background: white;
    border-top: 1px solid #e6e6e6;
    padding: 12px 20px;
    height: 72px;
    display: flex;
    justify-content: center;
}

.input-inner {
    width: 780px;
    max-width: calc(100% - 40px);
    display: flex;
    gap: 10px;
}

input.stTextInput {
    border-radius: 12px !important;
    height: 48px;
}

.send-btn {
    background: #16a05c;
    border-radius: 10px;
    border: none;
    padding: 0 18px;
    color: white;
    font-size: 15px;
    cursor: pointer;
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

    if "chat" not in st.session_state:
        st.session_state.chat = [{
            "role": "ai",
            "content": "Hello! I have loaded your CRM data. What would you like to know about Acme Corporation?",
            "timestamp": time.strftime("%I:%M %p")
        }]

    if "lead" not in st.session_state:
        st.session_state.lead = {
            "name": "Acme Corporation",
            "score": "0%",
            "status": "Qualification"
        }

    lead = st.session_state.lead

    # ===== PAGE WRAPPER =====
    st.markdown("<div class='page'>", unsafe_allow_html=True)
    st.markdown("<div class='chat-column'>", unsafe_allow_html=True)

    # ---- Lead Summary ----
    st.markdown(f"""
    <div class='lead-summary'>
        <div style='font-size:13px;color:#777;'>Lead</div>
        <div style='font-size:20px;font-weight:700;'>{lead['name']}</div>
        <div style='font-size:13px;color:#888;margin-top:4px;'>
            Status: {lead['status']} • Score: {lead['score']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---- Chat Messages ----
    for msg in st.session_state.chat:
        bubble = "msg-user" if msg["role"] == "user" else "msg-ai"
        st.markdown(
            f"<div class='{bubble}'>{msg['content']}<div class='time'>{msg['timestamp']}</div></div>",
            unsafe_allow_html=True
        )

    st.markdown("</div></div>", unsafe_allow_html=True)  # close column + page


    # ===== INPUT BAR =====
    st.markdown("<div class='input-bar'><div class='input-inner'>", unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        left, right = st.columns([8,1])

        with left:
            user_msg = st.text_input("", placeholder="Message SalesBuddy...")

        with right:
            send = st.form_submit_button("Send")

        if send and user_msg.strip():
            st.session_state.chat.append({
                "role": "user",
                "content": user_msg,
                "timestamp": time.strftime("%I:%M %p")
            })

            reply = "Processing your request..."  # Placeholder response
            st.session_state.chat.append({
                "role": "ai",
                "content": reply,
                "timestamp": time.strftime("%I:%M %p")
            })

            st.rerun()

    st.markdown("</div></div>", unsafe_allow_html=True)
