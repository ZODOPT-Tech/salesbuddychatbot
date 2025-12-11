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


# ================== CSS (ChatGPT-Style, adjusted) =====================
CSS = """
<style>
/* Force full viewport usage and remove page-level scroll */
html, body, .stApp, .block-container {
    height: 100vh !important;
    margin: 0;
    padding: 0;
    overflow: hidden; /* prevents browser scrollbar */
    background: #ffffff;
    font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
}

/* Header */
.top-header {
    position: fixed;
    top: 0;
    left: 0; right: 0;
    background: #ffffff;
    border-bottom: 1px solid #e6e6e6;
    padding: 12px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 999;
    height: 64px;
    box-sizing: border-box;
}

.top-title {
    font-size: 20px;
    font-weight: 700;
    color: #111;
}

.brand-logo {
    font-size: 18px;
    font-weight: 800;
}
.brand-logo span:nth-child(1) { color: #ff3c0a; }
.brand-logo span:nth-child(2) { color: #00c48c; }

/* Layout: main area between header and input */
.page {
    position: absolute;
    top: 64px; /* header height */
    bottom: 72px; /* input bar height */
    left: 0;
    right: 0;
    overflow: hidden; /* prevents page scrolling, chat area will scroll */
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 20px;
    box-sizing: border-box;
}

/* Narrow centered column for chat */
.chat-column {
    width: 780px;
    max-width: calc(100% - 40px);
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

/* Lead summary - compact, no right-side three-dot */
.lead-summary {
    background: white;
    border-radius: 12px;
    padding: 14px 18px;
    border: 1px solid #efefef;
    display: flex;
    align-items: center;
    gap: 14px;
    box-shadow: 0 1px 0 rgba(0,0,0,0.02);
}

/* hide any right-side action (three dots) in lead summary */
.lead-summary .lead-actions { display: none !important; }

/* Chat area: takes remaining vertical space and internally scrolls */
.chat-area {
    flex: 1 1 auto;
    overflow-y: auto;
    padding-right: 6px;
    scroll-behavior: smooth;
}

/* Message bubbles */
.msg-ai, .msg-user {
    padding: 14px 18px;
    border-radius: 14px;
    font-size: 16px;
    line-height: 1.5;
    margin-bottom: 14px;
    width: fit-content;
    max-width: 86%;
    box-sizing: border-box;
}

/* AI bubble (light gray) */
.msg-ai {
    background: #f7f7f8;
    border: 1px solid #ececec;
    color: #111;
    border-bottom-left-radius: 6px;
}

/* User bubble (greenish) - aligned right */
.msg-user {
    background: #dfffe7;
    border: 1px solid #b2f7c6;
    margin-left: auto;
    color: #111;
    border-bottom-right-radius: 6px;
}

/* Timestamp */
.time {
    font-size: 11px;
    opacity: 0.65;
    margin-top: 6px;
}

/* Input Bar fixed at bottom */
.input-bar {
    position: fixed;
    bottom: 0;
    left: 0; right: 0;
    background: white;
    padding: 10px 16px;
    border-top: 1px solid #e6e6e6;
    height: 72px;
    box-sizing: border-box;
    z-index: 999;
    display: flex;
    justify-content: center;
    align-items: center;
}

.input-inner {
    display: flex;
    gap: 10px;
    width: 780px;
    max-width: calc(100% - 40px);
    align-items: center;
}

.input-field {
    flex: 1 1 auto;
    height: 48px;
    border-radius: 12px;
    border: 1px solid #e8e8e8;
    padding: 0 16px;
    font-size: 15px;
}

.send-btn {
    background: #16a05c;
    border-radius: 12px;
    color: white;
    padding: 10px 16px;
    font-size: 15px;
    cursor: pointer;
    border: none;
}

/* small screens adjustments */
@media (max-width: 820px) {
    .chat-column, .input-inner { width: calc(100% - 32px); }
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
    # attempt to load data safely; if it fails we continue (UI unaffected)
    try:
        df = load_data()
    except Exception:
        df = None

    credits = get_remaining_api_credits()

    if "chat" not in st.session_state:
        st.session_state.chat = [{
            "role":"ai",
            "content":"Hello! I have loaded your CRM data. What would you like to know about the current lead?",
            "timestamp": time.strftime("%I:%M %p")
        }]

    if "lead" not in st.session_state:
        st.session_state.lead = {
            "name":"Acme Corporation",
            "score":"0%",
            "status":"Qualification"
        }

    lead = st.session_state.lead

    # ===== HEADER =====
    st.markdown(f"""
    <div class="top-header">
        <div class="top-title">SalesBuddy</div>
        <div class="brand-logo"><span>zod</span><span>opt</span></div>
    </div>
    """, unsafe_allow_html=True)

    # ===== PAGE WRAPPER (header -> page -> input) =====
    st.markdown("<div class='page'>", unsafe_allow_html=True)

    # centered chat column
    st.markdown("<div class='chat-column'>", unsafe_allow_html=True)

    # ---- Lead summary (compact) ----
    st.markdown(f"""
    <div class='lead-summary'>
        <div style='display:flex;flex-direction:column;'>
            <div style='font-size:13px;color:#666;'>Lead</div>
            <div style='font-size:17px;font-weight:700;color:#111;'>{lead['name']}</div>
            <div style='font-size:13px;color:#888;margin-top:6px;'>Status: {lead['status']} • Score: {lead['score']}</div>
        </div>
        <div class='lead-actions' style='margin-left:auto;'></div>
    </div>
    """, unsafe_allow_html=True)

    # ---- Chat area (scrolls internally) ----
    st.markdown("<div class='chat-area'>", unsafe_allow_html=True)

    for msg in st.session_state.chat:
        bubble_class = "msg-user" if msg["role"] == "user" else "msg-ai"
        st.markdown(
            f"<div class='{bubble_class}'>{msg['content']}<div class='time'>{msg.get('timestamp','')}</div></div>",
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)  # close chat-area
    st.markdown("</div>", unsafe_allow_html=True)  # close chat-column
    st.markdown("</div>", unsafe_allow_html=True)  # close page

    # ===== INPUT BAR (fixed) =====
    st.markdown("""
    <div class="input-bar">
      <div class="input-inner">
    """, unsafe_allow_html=True)

    # Use a simple form with text input and button
    with st.form("chat_form", clear_on_submit=True):
        # Use columns to align the input and button (but keep CSS input-inner)
        cols = st.columns([18, 2])
        with cols[0]:
            user_msg = st.text_input("", placeholder="Message SalesBuddy...", key="input_msg")
        with cols[1]:
            send = st.form_submit_button("Send")

        if send and user_msg:
            # append user message
            st.session_state.chat.append({
                "role": "user",
                "content": user_msg,
                "timestamp": time.strftime("%I:%M %p")
            })

            # optionally call Gemini here (non-blocking suggestion)
            # if api_key:
            #     try:
            #         ai_reply = ask_gemini(user_msg, api_key)
            #     except Exception as e:
            #         ai_reply = "Sorry — failed to fetch response."
            # else:
            #     ai_reply = "No API key configured."

            # For now, echo simple placeholder response (or you can uncomment real call)
            ai_reply = "Thanks — noted. (This is a placeholder response.)"

            st.session_state.chat.append({
                "role": "ai",
                "content": ai_reply,
                "timestamp": time.strftime("%I:%M %p")
            })

            # rerun so chat-area updates and automatically scrolls (browser will position at top of chat-area scroll)
            st.experimental_rerun()

    st.markdown("""
      </div>
    </div>
    """, unsafe_allow_html=True)
