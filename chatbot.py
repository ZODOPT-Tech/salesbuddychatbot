import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
import boto3 
from botocore.exceptions import ClientError
from io import BytesIO
import json
import re 
import random # Used for the dummy API count

# ---------------------- CONFIG & FUNCTIONS (Unchanged) --------------------------
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
DISQUALIFYING_STATUSES = ["Disqualified", "Closed - Lost", "Junk Lead"]

# Dummy function for real-time API credit calculation
def get_remaining_api_credits():
    """Simulates fetching real-time API credits or a calculated limit."""
    # In a real app, this would call a usage tracking API or query a database.
    # For demonstration, we'll return a random number within a range.
    return random.randint(1500, 3000)

# (get_secret, load_data_from_s3, filter_data_context, ask_gemini functions are kept the same)

@st.cache_resource
def get_secret(secret_name, region_name, key_name):
    try:
        session = boto3.session.Session()
        client = session.client('secretsmanager', region_name=region_name)
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        if 'SecretString' in get_secret_value_response:
            secret = json.loads(get_secret_value_response['SecretString'])
            return secret.get(key_name), None
        else:
            return None, "❌ Secret is not a JSON string."
    except ClientError as e:
        error_map = {'ResourceNotFoundException': f"Secret **{secret_name}** not found."}
        return None, f"❌ Secrets Manager Error: {error_map.get(e.response['Error']['Code'], str(e))}"
    except Exception as e:
        return None, f"❌ Unexpected error in Secrets Manager: {e}"


@st.cache_data(ttl=600)
def load_data_from_s3(bucket_name, file_key, required_cols):
    try:
        s3 = boto3.client('s3')
        obj = s3.get_object(Bucket=bucket_name, Key=file_key)
        df = pd.read_excel(BytesIO(obj['Body'].read()))
        df.columns = df.columns.str.strip()
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            return None, f"❌ Missing essential columns: **{', '.join(missing)}**"
        df_filtered = df[required_cols]
        df_filtered['Annual Revenue'] = pd.to_numeric(df_filtered['Annual Revenue'], errors='coerce')
        return df_filtered, None
    except Exception as e:
        return None, f"❌ Error reading/processing data: {e}"


def filter_data_context(df, query):
    df_working = df.copy()
    query_lower = query.lower()
    key_phrases = ["best leads", "hot leads", "convertible", "potential", "possibility", "high value"]
    if any(p in query_lower for p in key_phrases):
        df_working = df_working[~df_working["Lead Status"].isin(DISQUALIFYING_STATUSES)]
    locations = ["bangalore", "bengaluru", "delhi", "new york", "london", "texas", "india"]
    loc_match = next((loc for loc in locations if loc in query_lower), None)
    if loc_match:
        mask = (df_working["City"].astype(str).str.lower().str.contains(loc_match, na=False) |
                df_working["State"].astype(str).str.lower().str.contains(loc_match, na=False) |
                df_working["Country"].astype(str).str.lower().str.contains(loc_match, na=False))
        df_working = df_working[mask]
        if df_working.empty:
            df_working = df.head(0) 
    return df_working.to_csv(index=False, sep="\t")


def ask_gemini(question, data_context, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(GEMINI_MODEL) 
        prompt = f"""You are ZODOPT Sales Buddy. You strictly analyze ONLY the following tab-separated CRM lead data.
Do not guess or hallucinate any values outside the dataset.
--- DATASET ---
{data_context}
--- QUESTION ---
{question}
Provide structured bullet-point insights, using the data fields provided."""
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Gemini API Error: {e}"


# ---------------------- PROFESSIONAL CHAT CSS ----------------------
CHAT_CSS = """
<style>
/* App Background & Layout */
.stApp {
    background-color: #f0f2f6; /* Very light gray */
}

/* Hide Streamlit Header */
[data-testid="stHeader"] { visibility: hidden; }

/* Main Chat Container Size */
.main .block-container {
    max-width: 700px;
    padding: 0px 1rem 0px 1rem;
    margin-left: auto;
    margin-right: auto;
}

/* --- HEADER STYLES --- */
.salesbuddy-header {
    background-color: #1abc9c; /* Teal Green Header */
    color: white;
    padding: 15px 20px;
    border-radius: 10px 10px 0 0;
    margin: -16px -16px 0 -16px; /* Extend to fill container width */
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

.header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header-profile {
    display: flex;
    align-items: center;
}

.profile-icon {
    font-size: 20px;
    margin-right: 10px;
}

.header-title {
    font-size: 20px;
    font-weight: 700;
}

.header-subtitle {
    font-size: 14px;
    font-weight: 400;
    color: #e0f2f1; /* Lighter teal */
}

/* API Credit Display */
.api-credits {
    font-size: 14px;
    font-weight: 500;
    background-color: #16a085; /* Darker teal/green */
    padding: 5px 10px;
    border-radius: 15px;
    margin-top: 10px;
    width: fit-content;
}

/* --- CHAT HISTORY STYLES --- */
.chat-history-container {
    height: calc(100vh - 180px); /* Fill remaining space (100vh - header/input height) */
    overflow-y: auto;
    padding-right: 15px;
    margin-top: 20px;
    padding-bottom: 70px; /* Space for fixed input bar */
}

.chat-bubble-user {
    background: #d8f5d0; /* Soft user green */
    padding: 12px;
    border-radius: 15px 15px 0px 15px;
    margin: 10px 0 10px auto;
    max-width: 80%;
    width: fit-content;
    text-align: left;
    color: #333;
    font-size: 15px;
}

.chat-bubble-ai {
    background: #ffffff;
    padding: 12px;
    border-radius: 15px 15px 15px 0px;
    margin: 10px auto 10px 0;
    max-width: 80%;
    width: fit-content;
    border: 1px solid #eee;
    color: #333;
    font-size: 15px;
}

/* --- FIXED INPUT STYLES --- */
.stTextInput:has(input[type="text"]) {
    position: fixed;
    bottom: 0px;
    max-width: 700px;
    width: 100%;
    margin-left: auto;
    margin-right: auto;
    z-index: 1000;
    background-color: #f0f2f6; 
    padding: 10px 0;
    box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
}

.stTextInput:has(input[type="text"]) input {
    border-radius: 25px !important;
    padding: 12px 20px !important;
    border: 1px solid #1abc9c !important; /* Teal border on input */
    box-shadow: 0 0 5px rgba(26, 188, 156, 0.2);
}

/* Ensure the full width of the block container is respected for input */
div[data-testid="stVerticalBlock"] > div:nth-child(4) {
    max-width: 700px;
    margin-left: auto;
    margin-right: auto;
}
</style>
"""

st.markdown(CHAT_CSS, unsafe_allow_html=True)


# ---------------------- CHATBOT RENDER FUNCTION ----------------------

def render(navigate, user_data):

    # --- 1. Load API Key and Data ---
    gemini_api_key, secret_msg = get_secret(GEMINI_SECRET_NAME, AWS_REGION, GEMINI_SECRET_KEY)
    if gemini_api_key is None:
        st.error(secret_msg)
        st.stop()
    
    df_filtered, load_msg = load_data_from_s3(S3_BUCKET_NAME, S3_FILE_KEY, REQUIRED_COLS)
    if df_filtered is None:
        st.error(load_msg)
        st.stop()
    
    # --- 2. CUSTOM HEADER (API Count and Profile) ---
    remaining_credits = get_remaining_api_credits()

    st.markdown(f"""
        <div class='salesbuddy-header'>
            <div class='header-row'>
                <div class='header-profile'>
                    <span class='profile-icon'>🤖</span>
                    <div>
                        <div class='header-title'>SalesBuddy Agent</div>
                        <div class='header-subtitle'>Logged in as: {user_data.get("full_name", "User")}</div>
                    </div>
                </div>
                <button style="background:none; border:none; color:white; font-size:24px;" 
                        onclick="window.parent.postMessage('{{type: \"streamlit:setComponentValue\", value: \"logout\"}}', '*')"
                        title="Logout">
                    🚪
                </button>
            </div>
            <div class='api-credits'>
                API Credits Remaining: {remaining_credits:,}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # --- 3. CHAT HISTORY DISPLAY ---
    
    # Create an empty container where the chat history will be rendered
    chat_placeholder = st.empty()

    # Render the chat history into the container
    with chat_placeholder.container():
        st.markdown("<div class='chat-history-container'>", unsafe_allow_html=True)
        for msg in st.session_state.chat:
            if msg["role"] == "user":
                st.markdown(f"<div class='chat-bubble-user'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-bubble-ai'>{msg['content']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Scroll-to-bottom hack (requires a tiny delay/rerun)
        st.markdown(
            """<script>
            var chatHistory = document.querySelector('.chat-history-container');
            if (chatHistory) {
                chatHistory.scrollTop = chatHistory.scrollHeight;
            }
            </script>""", unsafe_allow_html=True
        )

    # --- 4. FIXED INPUT BAR ---
    
    # The input needs to be outside the chat history container to be fixed at the bottom
    query = st.chat_input("Ask about your leads (e.g., 'hot leads in Texas', 'status breakdown')...")
    
    if query:
        # Append user message
        st.session_state.chat.append({"role": "user", "content": query})
        
        # Process the query
        with st.spinner("Analyzing data and generating insights..."):
            data_ctx = filter_data_context(df_filtered, query)
            reply = ask_gemini(query, data_ctx, gemini_api_key)
            st.session_state.chat.append({"role": "ai", "content": reply})
        
        # Rerun to display the new messages and trigger the scroll-down hack
        st.rerun()

    # --- 5. Logout Button Hack (Simple way to trigger navigation from within this module) ---
    # The header button is a simple HTML button. If you need a more explicit Streamlit button:
    # if st.sidebar.button("Logout"):
    #     st.session_state.logged_in = False
    #     navigate("login")
    
    # We must ensure the chat history container is sufficiently tall to allow the fixed input bar to sit nicely.
    # The CSS takes care of the sizing.
