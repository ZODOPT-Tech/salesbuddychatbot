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
    # Simplified filtering...
    return df_working.to_csv(index=False, sep="\t")

def ask_gemini(question, data_context, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(GEMINI_MODEL) 
        prompt = f"""You are ZODOPT Sales Buddy. Analyze ONLY the following tab-separated CRM lead data.
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
    scrollbar-width: none; /* Hide scrollbar for Firefox */
    -ms-overflow-style: none; /* Hide scrollbar for IE and Edge */
    z-index: 180; /* Below headers */
    position: fixed;
    background-color: #f0f2f6;
    width: 100%;
    max-width: 800px;
    border-bottom: 1px solid #ddd;
}
.chip-bar-container::-webkit-scrollbar {
    display: none; /* Hide scrollbar for Chrome, Safari, and Opera */
}

.chip {
    display: inline-block;
    padding: 8px 15px;
    margin-right: 10px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    background-color: #ecf0f1; /* Default light chip */
    color: #333;
    border: 1px solid #bdc3c7;
    transition: background-color 0.2s;
}

.chip-active {
    background-color: #e8daef !important; /* Purple active */
    color: #8e44ad !important;
    border-color: #8e44ad !important;
}

/* --- CHAT HISTORY CONTAINER --- */
.chat-history-container {
    padding: 200px 20px 70px 20px; /* Padding to clear fixed headers and fixed input */
    min-height: calc(100vh);
    overflow-y: auto;
}

/* --- CHAT BUBBLES --- */
.chat-bubble-user {
    background: #32CD32; /* User Green bubble */
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
    background: #ffffff; /* AI White bubble */
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
    color: #999;
    margin-top: -5px;
    text-align: right;
    display: block;
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

.stTextInput input {
    border: none !important;
    padding: 10px 0 !important;
    font-size: 16px !important;
    flex-grow: 1;
}

.send-icon {
    font-size: 28px;
    color: #32CD32; /* Green send icon */
    cursor: pointer;
    margin-left: 10px;
}
</style>
"""

st.markdown(CHAT_CSS, unsafe_allow_html=True)

# ---------------------- SESSION STATE MANAGEMENT ----------------------

# Ensure st.session_state.chat exists and has data for UI to work
if "chat" not in st.session_state:
    st.session_state.chat = [
        {"role": "ai", "content": "Hello! I have loaded your CRM data. What would you like to know about Acme Corporation?"},
        {"role": "user", "content": "Sounds good!", "timestamp": "10:32 AM"}
    ]
    
# Mock data for the target lead/company
if "target_lead" not in st.session_state:
    st.session_state.target_lead = {
        "name": "Acme Corporation",
        "score": "0%",
        "status": "Qualification"
    }
    
# Mock data for the action chips
ACTION_CHIPS = ["Qualification", "Needs Analysis", "Proposal/Price Quote", "Negotiation/Review", "Closed Won"]


# ---------------------- CHATBOT RENDER FUNCTION ----------------------

def render(navigate, user_data):

    # --- 1. Load API Key and Data (Same as before) ---
    gemini_api_key, secret_msg = get_secret(GEMINI_SECRET_NAME, AWS_REGION, GEMINI_SECRET_KEY)
    if gemini_api_key is None:
        st.error(secret_msg)
        st.stop()
    
    df_filtered, load_msg = load_data_from_s3(S3_BUCKET_NAME, S3_FILE_KEY, REQUIRED_COLS)
    if df_filtered is None:
        st.error(load_msg)
        st.stop()
    
    # --- 2. FIXED HEADER (Top Bar) ---
    
    # Place header content inside a container to control max width
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
                        <span class='logout-icon' title='Logout' onclick="window.parent.postMessage('{{type: \"streamlit:setComponentValue\", value: \"logout\"}}', '*')">
                            &#x235F; 
                        </span>
                    </div>
                </div>
                <div class='api-credits-line'>
                    Total API Credits left **{get_remaining_api_credits():,}**
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    # --- 3. FIXED HEADER (Target Lead/Company) ---
    with st.container():
        st.markdown(f"""
            <div class='fixed-header-target'>
                <div class='target-row'>
                    <div style='display:flex; align-items:center;'>
                        <span style='font-size:24px; color:#666; margin-right:15px; cursor:pointer;'>&#x2B05;</span>
                        <div class='target-avatar'>A</div>
                        <div>
                            <div class='target-name'>{st.session_state.target_lead['name']}</div>
                            <div class='target-score'>Score: {st.session_state.target_lead['score']}</div>
                        </div>
                    </div>
                    <span style='font-size:24px; color:#666; cursor:pointer;'>&#x22EE;</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # --- 4. FIXED ACTION CHIP BAR ---
    with st.container():
        st.markdown("<div class='chip-bar-container'>", unsafe_allow_html=True)
        cols = st.columns(len(ACTION_CHIPS))
        
        for i, chip in enumerate(ACTION_CHIPS):
            # Use a button to capture click, and hide it using CSS to show the custom chip
            active_class = "chip-active" if chip == st.session_state.target_lead['status'] else ""
            
            # The HTML/JS hack is complex here, so we will use a simplified approach
            # where the button acts as the clickable element inside the container.
            if cols[i].button(chip, key=f"chip_{i}"):
                st.session_state.target_lead['status'] = chip
                st.session_state.chat.append({"role": "user", "content": f"Update the lead status to '{chip}' and provide next steps."})
                st.rerun()

            # Apply the custom chip styling via HTML injection (Streamlit hack)
            st.markdown(f"""
                <script>
                    var button = window.parent.document.querySelector('[data-testid="stButton"] button:contains("{chip}")');
                    if (button) {{
                        button.classList.add('chip');
                        if ('{active_class}' === 'chip-active') {{
                            button.classList.add('chip-active');
                        }}
                    }}
                </script>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # --- 5. CHAT HISTORY DISPLAY ---
    
    # This container sits below all fixed headers
    st.markdown("<div class='chat-history-container'>", unsafe_allow_html=True)
    for msg in st.session_state.chat:
        timestamp = msg.get("timestamp", pd.Timestamp.now().strftime("%I:%M %p"))
        
        if msg["role"] == "user":
            st.markdown(f"""
                <div class='chat-bubble-user'>
                    {msg['content']}
                    <span class='chat-timestamp' style='color:#a6e8b2; margin-top:5px; text-align:right;'>{timestamp}</span>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class='chat-bubble-ai'>
                    {msg['content']}
                    <span class='chat-timestamp' style='text-align:left;'>{timestamp}</span>
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
                # Use a submit button that acts as the send icon
                submitted = st.form_submit_button("▶", key="send_button_icon")

        if submitted and query:
            # Append user message with current time
            st.session_state.chat.append({"role": "user", "content": query, "timestamp": pd.Timestamp.now().strftime("%I:%M %p")})
            
            # Process the query
            with st.spinner("Analyzing data..."):
                data_ctx = filter_data_context(df_filtered, query)
                reply = ask_gemini(query, data_ctx, gemini_api_key)
                # Append AI response
                st.session_state.chat.append({"role": "ai", "content": reply, "timestamp": pd.Timestamp.now().strftime("%I:%M %p")})
            
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
            }
            </script>
            """, unsafe_allow_html=True
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
