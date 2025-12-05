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

html, body {
    margin:0 !important;
    padding:0 !important;
}

.appview-container, .main, body {
    padding:0 !important;
    margin:0 !important;
}

.stApp {
    background:#f6f7fb;
    padding:0 !important;
    margin:0 !important;
}

/* remove block container padding */
.block-container {
    padding-top:0 !important;
    max-width:900px !important;
    margin:0 auto !important;
}

/* ===== Gradient Header ===== */
.gradient-header {
    position:fixed;
    top:0;
    left:0;
    right:0;
    max-width:900px;
    margin:auto;
    background:linear-gradient(90deg,#0066ff 0%,#7b00ff 100%);
    border-radius:0 0 26px 26px;
    padding:32px 36px;
    display:flex;
    justify-content:space-between;
    align-items:center;
    color:white;
    z-index:1000;
}

.header-title {
    font-size:38px;
    font-weight:800;
}

.logo-text {
    font-size:36px;
    font-weight:800;
}
.logo-text span:nth-child(1){ color:#ff3c0a; }
.logo-text span:nth-child(2){ color:#00c48c; }

/* Body starts below header */
.page-container {
    padding-top:160px;
    max-width:900px;
    margin:auto;
}

.credits-line {
    font-size:15px;
    color:#666;
    margin-bottom:14px;
}


/* ===== Lead Card ===== */
.lead-section {
    background:white;
    border-radius:14px;
    padding:20px 22px;
    display:flex;
    justify-content:space-between;
    align-items:center;
    border:1px solid #eee;
}

.lead-left {
    display:flex;
    gap:14px;
    align-items:center;
}

.lead-avatar {
    width:50px;
    height:50px;
    border-radius:50%;
    background:#854ce4;
    display:flex;
    align-items:center;
    justify-content:center;
    color:white;
    font-size:22px;
    font-weight:700;
}

.lead-name {
    font-size:19px;
    font-weight:700;
}

.lead-score {
    font-size:13px;
    color:#777;
}


/* ===== Chips Force Horizontal ===== */
.chip-bar {
    margin-top:18px;
    white-space:nowrap;
    display:flex;
    flex-direction:row;
    gap:12px;
    overflow-x:auto;
    scrollbar-width:none;
    padding-bottom:6px;
}

.chip-bar::-webkit-scrollbar {
    display:none;
}

/* streamlit button overrides */
[data-testid="stButton"] button {
    display:inline-flex !important;
    align-items:center;
    white-space:nowrap;
    padding:10px 22px !important;
    border-radius:22px !important;
    border:1px solid #ddd !important;
    background:#fff !important;
    font-size:15px !important;
}

[data-testid="stButton"] {
    margin:0 !important;
}

.chip-active button {
    background:#efe5ff !important;
    border:1px solid #8035ff !important;
    color:#8035ff !important;
}


/* ===== Chat ===== */
.chat-container {
    padding:20px 8px 100px 8px;
}

.msg-user {
    background:#16a05c;
    color:white;
    padding:10px 16px;
    border-radius:20px 20px 0 20px;
    max-width:65%;
    margin-left:auto;
    margin-bottom:16px;
}

.msg-ai {
    background:white;
    border:1px solid #eee;
    padding:10px 16px;
    border-radius:20px 20px 20px 0;
    max-width:65%;
    margin-bottom:16px;
}

.time-u {
    font-size:11px;
    text-align:right;
    margin-top:4px;
    opacity:0.8;
}

.time-ai {
    font-size:11px;
    color:#777;
    margin-top:4px;
}


/* ===== Input Bar ===== */
.input-bar {
    position:fixed;
    bottom:0;
    left:0;
    right:0;
    max-width:900px;
    margin:auto;
    background:white;
    border-top:1px solid #eee;
    padding:12px 14px;
}

.input-row {
    display:flex;
    gap:10px;
    align-items:center;
}

.send-btn {
    background:#16a05c;
    color:white;
    height:44px;
    width:44px;
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:18px;
    cursor:pointer;
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

    if "chat" not in st.session_state:
        st.session_state.chat = []

    if "lead" not in st.session_state:
        st.session_state.lead = {
            "name":"Acme Corporation",
            "score":"0%",
            "status":"Qualification"
        }

    lead = st.session_state.lead


    # ====== HEADER ======
    st.markdown("""
    <div class="gradient-header">
        <div class="header-title">SalesBuddy</div>
        <div class="logo-text"><span>zod</span><span>opt</span></div>
    </div>
    """, unsafe_allow_html=True)


    # ====== BODY WRAPPER ======
    st.markdown("<div class='page-container'>", unsafe_allow_html=True)


    # ====== CREDITS ======
    st.markdown(f"<div class='credits-line'>Total API Credits Left: {credits:,}</div>", unsafe_allow_html=True)


    # ====== LEAD CARD ======
    st.markdown(f"""
    <div class="lead-section">
        <div class="lead-left">
            <div class="lead-avatar">A</div>
            <div>
                <div class="lead-name">{lead['name']}</div>
                <div class="lead-score">Score: {lead['score']}</div>
            </div>
        </div>
        <div style="font-size:22px;color:#666;">⋮</div>
    </div>
    """, unsafe_allow_html=True)


    # ====== CHIPS ======
    st.markdown("<div class='chip-bar'>", unsafe_allow_html=True)
    for chip in ACTION_CHIPS:
        active_class = "chip-active" if chip == lead['status'] else ""
        with st.container():
            btn = st.button(chip, key=f"chip-{chip}")
            if btn:
                st.session_state.lead['status'] = chip

        if active_class:
            st.markdown(
                f"<style>[key='chip-{chip}']{{}} [key='chip-{chip}'] button{{background:#efe5ff !important;color:#8035ff !important;border-color:#8035ff !important;}}</style>",
                unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


    # ====== CHAT ======
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for msg in st.session_state.chat:
        if msg["role"]=="user":
            st.markdown(
                f"<div class='msg-user'>{msg['content']}<div class='time-u'>{msg['timestamp']}</div></div>",
                unsafe_allow_html=True)
        else:
            st.markdown(
                f"<div class='msg-ai'>{msg['content']}<div class='time-ai'>{msg['timestamp']}</div></div>",
                unsafe_allow_html=True)


    # ====== INPUT BAR ======
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='input-bar'>", unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([10,1])
        with col1:
            query = st.text_input("", placeholder="Type a message...")
        with col2:
            send = st.form_submit_button("▶")

        if send and query:
            st.session_state.chat.append({
                "role":"user",
                "content":query,
                "timestamp":time.strftime("%I:%M %p")
            })

    st.markdown("</div>", unsafe_allow_html=True)
