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

* { font-family:"Inter",sans-serif; }

.stApp { background:#f6f7fb; }

.block-container {
    padding:0 !important;
    max-width:900px;
}

/* ========= GRADIENT HEADER ========= */
.gradient-header {
    margin:20px auto 14px auto;
    width:100%;
    background:linear-gradient(90deg, #0066ff 0%, #7b00ff 100%);
    border-radius:22px;
    padding:28px 34px;
    display:flex;
    justify-content:space-between;
    align-items:center;
    color:white;
}

.header-title {
    font-size:34px;
    font-weight:700;
}

.logo-text {
    font-size:32px;
    font-weight:700;
}

.logo-text span:nth-child(1){ color:#ff3c0a; }
.logo-text span:nth-child(2){ color:#00c48c; }

.credits-line {
    font-size:13px;
    color:#666;
}


/* ========= LEAD SECTION ========= */
.lead-section {
    background:white;
    border-radius:12px;
    padding:18px 22px;
    display:flex;
    justify-content:space-between;
    align-items:center;
    border:1px solid #eee;
}

.lead-left { display:flex; gap:12px; align-items:center; }

.lead-avatar {
    width:44px;
    height:44px;
    border-radius:50%;
    background:#854ce4;
    display:flex;
    align-items:center;
    justify-content:center;
    color:white;
    font-size:20px;
    font-weight:700;
}

.lead-name {
    font-size:18px;
    font-weight:700;
}

.lead-score {
    font-size:12px;
    color:#777;
}


/* ========= CHIPS ========= */
.chip-bar {
    margin-top:14px;
    display:flex;
    gap:10px;
    overflow-x:auto;
    scrollbar-width:none;
}

.chip-bar::-webkit-scrollbar { display:none; }

.chip-btn {
    font-size:13px;
    padding:7px 18px;
    background:#f1f1f1;
    border-radius:18px;
    border:1px solid #ddd;
    cursor:pointer;
    white-space:nowrap;
}

.chip-active {
    background:#efe5ff;
    color:#8035ff;
    border:1px solid #8035ff;
}


/* ========= CHAT ========= */
.chat-container {
    padding:18px 8px 90px 8px;
}

.msg-user {
    background:#16a05c;
    color:white;
    padding:10px 16px;
    border-radius:18px 18px 0 18px;
    max-width:65%;
    margin-left:auto;
    margin-bottom:14px;
}

.msg-ai {
    background:white;
    border:1px solid #eee;
    padding:10px 16px;
    border-radius:18px 18px 18px 0;
    max-width:65%;
    margin-bottom:14px;
}

.time-u {
    font-size:10px;
    text-align:right;
    margin-top:4px;
    opacity:0.8;
}

.time-ai {
    font-size:10px;
    color:#777;
    margin-top:4px;
}


/* ========= INPUT BAR ========= */
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
    height:42px;
    width:42px;
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    cursor:pointer;
    font-size:18px;
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

    # Session state
    if "chat" not in st.session_state:
        st.session_state.chat = []

    if "lead" not in st.session_state:
        st.session_state.lead = {
            "name":"Acme Corporation",
            "score":"0%",
            "status":"Qualification"
        }

    lead = st.session_state.lead


    # ====== GRADIENT HEADER ======
    st.markdown(f"""
    <div class="gradient-header">
        <div class="header-title">SalesBuddy</div>
        <div class="logo-text">
            <span>zod</span><span>opt</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

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


    # ====== STATUS STAGE TABS ======
    st.markdown("<div class='chip-bar'>", unsafe_allow_html=True)

    for chip in ACTION_CHIPS:
        active = "chip-active" if chip == lead['status'] else ""
        if st.button(chip, key=f"chip-{chip}"):
            st.session_state.lead['status'] = chip

        st.markdown(
            f"<style>[key='chip-{chip}'] button{{padding:7px 18px;border-radius:18px;}}"
            "</style>",
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)


    # ====== CHAT AREA ======
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


    # ====== INPUT BOX ======
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
