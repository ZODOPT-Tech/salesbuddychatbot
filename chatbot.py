import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
import boto3 
from botocore.exceptions import ClientError
from io import BytesIO
import json
import re 
import random 
import time # For generating timestamps

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

def get_remaining_api_credits():
    """Simulates fetching real-time API credits."""
    return random.randint(1500, 3000)

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
    except Exception as e:
        return None, f"❌ Secrets Manager Error: {e}"

@st.cache_data(ttl=600)
def load_data_from_s3(bucket_name, file_key, required_cols):
    try:
        s3 = boto3.client('s3')
        obj = s3.get_object(Bucket=bucket_name, Key=file_key)
        df = pd.read_excel(BytesIO(obj['Body'].read()))
        df.columns = df.columns.str.strip()
        df_filtered = df[required_cols]
        df_filtered['Annual Revenue'] = pd.to_numeric(df_filtered['Annual Revenue'], errors='coerce')
        return df_filtered, None
    except Exception as e:
        return None, f"❌ Error reading/processing data: {e}"

def filter_data_context(df, query):
    df_working = df.copy()
    query_lower = query.lower()
    # Simplified filtering...
    return df_working.to_csv(index=False, sep="\t")

def ask_gemini(question, data_context, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(GEMINI_MODEL) 
        prompt = f"""You are ZODOPT Sales Buddy. Analyze ONLY the following tab-separated CRM lead data.
Do not guess or hallucinate any values outside the dataset.
--- DATASET ---
{data_context}
--- QUESTION ---
{question}
Provide structured bullet-point insights."""
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Gemini API Error: {e}"

# ---------------------- MODERN CHAT UI CSS ----------------------
CHAT_CSS = """
<style>
/* Base Streamlit Overrides */
.stApp {
    background-color: #f0f2f6; /* Light gray background, matching the image */
}
[data-testid="stHeader"] { visibility: hidden; }

/* Main Chat Container Sizing */
.main .block-container {
    max-width: 800px; 
    padding: 0;
    margin-left: auto;
    margin-right: auto;
}

/* --- FIXED HEADER/ACTION BAR --- */

/* Primary Header: SalesBuddy | Search | Logout */
.fixed-header-top {
    background-color: white;
    padding: 15px 20px 10px 20px;
    border-bottom: 1px solid #ddd;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    position: fixed;
    top: 0;
    width: 100%;
    max-width: 800px;
    z-index: 200;
}

.header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header-profile-info {
    font-size: 16px;
    color: #666;
    margin-top: -5px;
}

.icon-sales-buddy {
    font-size: 30px;
    color: #32CD32; /* Green avatar */
    margin-right: 10px;
}

.logout-icon, .search-icon {
    font-size: 24px;
    color: #666;
    margin-left: 15px;
    cursor: pointer;
}

/* API Credits Line */
.api-credits-line {
    font-size: 13px;
    color: #888;
    padding-top: 5px;
    padding-bottom: 5px;
}

/* Secondary Header: Target Lead/Company Info */
.fixed-header-target {
    background-color: white;
    padding: 10px 20px;
    border-bottom: 1px solid #eee;
    margin-top: 100px; /* Space needed for the top header */
    position: fixed;
    width: 100%;
    max-width: 800px;
    z-index: 190;
}

.target-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.target-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: #9b59b6; /* Purple/Blue avatar */
    color: white;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 18px;
    font-weight: 600;
    margin-right: 15px;
}

.target-name {
    font-size: 16px;
    font-weight: 600;
    color: #333;
}

.target-score {
    font-size: 13px;
    color: #888;
}

/* --- CHIP BAR STYLES --- */
.chip-bar-container {
    padding: 10px 0;
    margin-top: 150px; /* Space for both headers */
    white-space: nowrap;
    overflow-x: auto;
    overflow-y: hidden;
    scrollbar-width: none; 
    -ms-overflow-style: none;
    z-index: 180; 
    position: fixed;
    background-color: #f0f2f6;
    width: 100%;
    max-width: 800px;
    border-bottom: 1px solid #ddd;
}
.chip-bar-container::-webkit-scrollbar {
    display: none; 
}

.chip-wrapper {
    display: inline-flex;
    padding-left: 20px; /* Start padding for chips */
}

/* Base button style for chips */
.chip-bar-container button {
    display: inline-block;
    padding: 8px 15px !important;
    margin-right: 10px !important;
    border-radius: 20px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    background-color: #ecf0f1 !important; 
    color: #333 !important;
    border: 1px solid #bdc3c7 !important;
    min-width: fit-content;
    height: 38px;
}

.chip-active {
    background-color: #e8daef !important; 
    color: #8e44ad !important;
    border-color: #8e44ad !important;
}

/* --- CHAT HISTORY CONTAINER --- */
.chat-history-container {
    /* Padding to clear fixed headers (approx 180px) and fixed input (approx 70px) */
    padding: 190px 20px 70px 20px; 
    min-height: calc(100vh);
    overflow-y: auto;
}

/* --- CHAT BUBBLES --- */
.chat-bubble-user {
    background: #32CD32; 
    color: white;
    padding: 8px 15px;
    border-radius: 15px 15px 0px 15px;
    margin: 10px 0 10px auto;
    max-width: 60%;
    width: fit-content;
    text-align: left;
    font-size: 15px;
}

.chat-bubble-ai {
    background: #ffffff; 
    color: #333;
    padding: 8px 15px;
    border-radius: 15px 15px 15px 0px;
    margin: 10px auto 10px 0;
    max-width: 60%;
    width: fit-content;
    border: 1px solid #eee;
    font-size: 15px;
}
.chat-timestamp {
    font-size: 10px;
    color: rgba(255, 255, 255, 0.7); /* Lighter color for user timestamp */
    margin-top: 5px;
    text-align: right;
    display: block;
}
.chat-timestamp-ai {
    color: #999; /* Darker color for AI timestamp */
    text-align: left;
}


/* --- FIXED INPUT BAR --- */
.fixed-input-bar {
    position: fixed;
    bottom: 0px;
    width: 100%;
    max-width: 800px;
    background-color: white;
    padding: 10px 20px;
    box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    z-index: 200;
}

.input-container {
    display: flex;
    align-items: center;
}

/* Remove internal Streamlit styling for chat input */
div[data-testid="stForm"] > div > div > div > div > input {
    border: none !important;
    box-shadow: none !important;
    padding: 10px 0 !important;
    font-size: 16px !important;
}

.send-icon {
    font-size: 28px;
    color: #32CD32; 
    cursor: pointer;
    margin-left: 10px;
}
</style>
"""

st.markdown(CHAT_CSS, unsafe_allow_html=True)


# ---------------------- CHATBOT RENDER FUNCTION ----------------------

# 🔑 NOTE: The function signature is updated to accept ACTION_CHIPS
def render(navigate, user_data, ACTION_CHIPS):

    # --- 1. Load API Key and Data ---
    gemini_api_key, secret_msg = get_secret(GEMINI_SECRET_NAME, AWS_REGION, GEMINI_SECRET_KEY)
    if gemini_api_key is None:
        st.error(secret_msg)
        st.stop()
    
    df_filtered, load_msg = load_data_from_s3(S3_BUCKET_NAME, S3_FILE_KEY, REQUIRED_COLS)
    if df_filtered is None:
        st.error(load_msg)
        st.stop()
    
    # --- 2. FIXED HEADER (Top Bar) ---
    remaining_credits = get_remaining_api_credits()

    with st.container():
        st.markdown(f"""
            <div class='fixed-header-top'>
                <div class='header-row'>
                    <div style='display:flex; align-items:center;'>
                        <span class='icon-sales-buddy'>&#x1F464;</span> 
                        <div>
                            <div style='font-size:18px; font-weight:700; color:#333;'>SalesBuddy</div>
                            <div class='header-profile-info'>{user_data.get("full_name", "User")}</div>
                        </div>
                    </div>
                    <div>
                        <span class='search-icon' title='Search'>&#x1F50D;</span>
                        <span class='logout-icon' id='logout_btn' title='Logout'>&#x235F;</span>
                        <script>
                            document.getElementById('logout_btn').onclick = function() {{
                                // This script navigates back to login state via the session state mechanism in main.py
                                const data = JSON.stringify({{target: 'streamlit_app', type: 'set_session_state', key: 'logged_in', value: false}});
                                window.parent.postMessage(data, '*');
                                const data2 = JSON.stringify({{target: 'streamlit_app', type: 'set_session_state', key: 'page', value: 'login'}});
                                window.parent.postMessage(data2, '*');
                            }};
                        </script>
                    </div>
                </div>
                <div class='api-credits-line'>
                    Total API Credits left **{remaining_credits:,}**
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    # --- 3. FIXED HEADER (Target Lead/Company) ---
    with st.container():
        # Ensure target_lead exists in session state (initialized in main.py now)
        target_lead = st.session_state.get("target_lead", {"name": "No Lead Selected", "score": "--", "status": "Qualification"})
        
        st.markdown(f"""
            <div class='fixed-header-target'>
                <div class='target-row'>
                    <div style='display:flex; align-items:center;'>
                        <span style='font-size:24px; color:#666; margin-right:15px; cursor:pointer;'>&#x2B05;</span>
                        <div class='target-avatar'>A</div>
                        <div>
                            <div class='target-name'>{target_lead['name']}</div>
                            <div class='target-score'>Score: {target_lead['score']}</div>
                        </div>
                    </div>
                    <span style='font-size:24px; color:#666; cursor:pointer;'>&#x22EE;</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # --- 4. FIXED ACTION CHIP BAR ---
    with st.container():
        st.markdown("<div class='chip-bar-container'><div class='chip-wrapper'>", unsafe_allow_html=True)
        
        # Streamlit buttons are used for interactivity, CSS makes them look like chips
        for i, chip in enumerate(ACTION_CHIPS):
            active_class = "chip-active" if chip == target_lead['status'] else ""
            
            # Button click updates the status and triggers a query
            if st.button(chip, key=f"chip_{i}"):
                st.session_state.target_lead['status'] = chip
                
                # New user message for the status change
                st.session_state.chat.append({
                    "role": "user", 
                    "content": f"Update the lead status to '{chip}' and provide next steps.", 
                    "timestamp": pd.Timestamp.now().strftime("%I:%M %p")
                })
                
                # Ask Gemini
                with st.spinner(f"Analyzing required next steps for status: {chip}..."):
                    query = f"Provide next steps for the lead {target_lead['name']} now that the status is {chip}. Reference the lead data for context."
                    data_ctx = filter_data_context(df_filtered, query)
                    reply = ask_gemini(query, data_ctx, gemini_api_key)
                    st.session_state.chat.append({
                        "role": "ai", 
                        "content": reply, 
                        "timestamp": pd.Timestamp.now().strftime("%I:%M %p")
                    })
                st.rerun()

            # Apply the active class using JavaScript hack after the button renders
            if active_class:
                st.markdown(f"""
                    <script>
                        var button = window.parent.document.querySelector('[data-testid="stButton"] button:contains("{chip}")');
                        if (button) {{
                            button.classList.add('chip-active');
                        }}
                    </script>
                """, unsafe_allow_html=True)

        st.markdown("</div></div>", unsafe_allow_html=True) # Close chip-wrapper and chip-bar-container

    # --- 5. CHAT HISTORY DISPLAY ---
    
    # This container sits below all fixed headers
    st.markdown("<div class='chat-history-container'>", unsafe_allow_html=True)
    for msg in st.session_state.chat:
        timestamp = msg.get("timestamp", time.strftime("%I:%M %p")) # Use time.strftime for simplicity
        
        if msg["role"] == "user":
            st.markdown(f"""
                <div class='chat-bubble-user'>
                    {msg['content']}
                    <span class='chat-timestamp'>{timestamp}</span>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class='chat-bubble-ai'>
                    {msg['content']}
                    <span class='chat-timestamp chat-timestamp-ai'>{timestamp}</span>
                </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Scroll-to-bottom hack
    st.markdown(
        """<script>
        var chatHistory = window.parent.document.querySelector('.chat-history-container');
        if (chatHistory) {
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }
        </script>""", unsafe_allow_html=True
    )

    # --- 6. FIXED INPUT BAR ---
    
    with st.container():
        st.markdown("<div class='fixed-input-bar'>", unsafe_allow_html=True)
        with st.form(key='chat_input_form', clear_on_submit=True):
            col_input, col_send = st.columns([10, 1])
            
            with col_input:
                query = st.text_input("", placeholder="Type a message...", key="final_query_input", label_visibility="collapsed")
            
            with col_send:
                submitted = st.form_submit_button("▶", key="send_button_icon")

        if submitted and query:
            # Append user message with current time
            st.session_state.chat.append({"role": "user", "content": query, "timestamp": time.strftime("%I:%M %p")})
            
            # Process the query
            with st.spinner("Analyzing data..."):
                data_ctx = filter_data_context(df_filtered, query)
                reply = ask_gemini(query, data_ctx, gemini_api_key)
                # Append AI response
                st.session_state.chat.append({"role": "ai", "content": reply, "timestamp": time.strftime("%I:%M %p")})
            
            st.rerun()

        # Apply CSS to the send button to make it look like an icon
        st.markdown(
            """
            <script>
            var sendButton = window.parent.document.querySelector('#send_button_icon');
            if (sendButton) {
                sendButton.style.backgroundColor = 'white';
                sendButton.style.color = '#32CD32';
                sendButton.style.border = 'none';
                sendButton.style.fontSize = '24px';
                sendButton.style.height = '40px';
                sendButton.style.width = '40px';
                sendButton.style.borderRadius = '50%';
                sendButton.style.fontWeight = '700';
                sendButton.style.display = 'flex';
                sendButton.style.alignItems = 'center';
                sendButton.style.justifyContent = 'center';
                // Adjust position to align with input field
                sendButton.parentElement.style.marginTop = '-5px';
            }
            </script>
            """, unsafe_allow_html=True
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
