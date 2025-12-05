import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
import base64
import mimetypes
import boto3 
from botocore.exceptions import ClientError
from io import BytesIO
import json
import tempfile 
import re 

# ---------------------- CONFIG --------------------------
# Set these variables to match your AWS setup
S3_BUCKET_NAME = "zodopt"
S3_FILE_KEY = "Leaddata/Leads by Status.xlsx" 

# --- AWS Secrets Manager Configuration (Match image_dc3c22.png) ---
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

# Initialize chat status flag (used to switch between "New Chat" and "Active Chat" views)
if "chat_initiated" not in st.session_state:
    st.session_state.chat_initiated = False

# ---------------------- CSS FOR CHAT UI --------------------------
CHAT_CSS = """
<style>
/* Streamlit main background (clean white/light gray for professional look) */
.stApp {
    background-color: #f5f7fa; 
}

/* Hide the header and Streamlit branding for a cleaner app feel */
[data-testid="stHeader"] { visibility: hidden; }

/* Main app container styling to simulate a focused chat window */
.main .block-container {
    max-width: 700px; /* Limit width for chat experience */
    padding: 0px 1rem 0px 1rem;
    margin-left: auto;
    margin-right: auto;
}

/* CUSTOM HEADER */
.salesbuddy-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 0;
    border-bottom: 1px solid #eee;
    margin-bottom: 15px;
}

.salesbuddy-header-left {
    display: flex;
    align-items: center;
}

.profile-icon {
    font-size: 24px;
    margin-right: 10px;
    color: #32CD32; /* Green from the original image */
}

.header-title {
    font-size: 18px;
    font-weight: 600;
    color: #333;
}

.header-subtitle {
    font-size: 14px;
    color: #777;
    margin-top: -5px;
}

.search-icon {
    font-size: 24px;
    color: #777;
    cursor: pointer;
}

/* Back Button/New Chat Line */
.back-to-chat {
    display: flex;
    align-items: center;
    font-size: 16px;
    font-weight: 500;
    color: #555;
    margin-bottom: 20px;
}

/* Centered Search Input Field (Mimics the 'Enter company or person's name...' bar for NEW CHAT) */
.centered-input-bar {
    background-color: #f0f2f6; 
    border-radius: 25px;
    padding: 10px 15px;
    display: flex;
    align-items: center;
    margin-bottom: 20px;
}

.centered-input-bar input {
    background: none;
    border: none;
    outline: none;
    width: 100%;
    margin-left: 10px;
    font-size: 16px;
    color: #333;
}

/* Start Chat Button (Primary Green) */
.stButton button {
    background-color: #32CD32 !important; 
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
}

.stButton button:hover {
    background-color: #27ae60 !important;
}

/* Suggested Contacts */
.suggested-contact-item {
    display: flex;
    align-items: center;
    padding: 10px 15px;
    background-color: #fff;
    border-radius: 10px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    margin-bottom: 10px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.suggested-contact-item:hover {
    background-color: #f8f8f8;
}

.contact-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: #32CD32;
    color: white;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 18px;
    font-weight: 600;
    margin-right: 15px;
}

.contact-name {
    font-size: 16px;
    color: #333;
    font-weight: 500;
}

/* CHAT HISTORY STYLES */

/* Container for scrollable chat history */
.chat-history-container {
    height: 60vh; /* Fixed height for history */
    overflow-y: auto; /* Make history scrollable */
    padding-right: 15px;
    margin-bottom: 10px;
}

.chat-bubble-user {
    background: #e1ffc7; /* Light green/user color */
    padding: 12px;
    border-radius: 15px 15px 0px 15px;
    margin: 10px 0 10px auto;
    max-width: 85%;
    width: fit-content;
    text-align: left;
    color: #333;
}

.chat-bubble-ai {
    background: #ffffff; /* White/AI color */
    padding: 12px;
    border-radius: 15px 15px 15px 0px;
    margin: 10px auto 10px 0;
    max-width: 85%;
    width: fit-content;
    border: 1px solid #eee;
    color: #333;
}

/* Chat Input Bar at the Bottom */
.stTextInput:has(input[type="text"]) {
    position: fixed;
    bottom: 0px;
    max-width: 700px;
    width: 100%;
    margin-left: auto;
    margin-right: auto;
    z-index: 1000;
    background-color: #f5f7fa; /* Match app background */
    padding: 10px 0;
    box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
}

.stTextInput:has(input[type="text"]) input {
    border-radius: 25px !important;
    padding: 12px 20px !important;
    border: 1px solid #ddd !important;
}

/* Ensure the full width of the block container is respected */
div[data-testid="stVerticalBlock"] > div:nth-child(4) {
    max-width: 700px;
    margin-left: auto;
    margin-right: auto;
}

</style>
"""

st.markdown(CHAT_CSS, unsafe_allow_html=True)


# ---------------------- FUNCTIONS: AWS & DATA LOADING --------------------------

# (Keep get_secret, load_data_from_s3, filter_data_context, ask_gemini unchanged)

@st.cache_resource
def get_secret(secret_name, region_name, key_name):
    """Fetches a specific key's value from a secret stored in AWS Secrets Manager."""
    try:
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        if 'SecretString' in get_secret_value_response:
            secret = json.loads(get_secret_value_response['SecretString'])
            return secret.get(key_name), None
        else:
            return None, "❌ Secret is not a JSON string (binary secret not supported for API Key)."
    except ClientError as e:
        error_map = {
            'ResourceNotFoundException': f"Secret **{secret_name}** not found.",
            'InvalidRequestException': "Invalid request to Secrets Manager.",
            'InvalidParameterException': "Invalid parameter in Secrets Manager request.",
        }
        return None, f"❌ Secrets Manager Error: {error_map.get(e.response['Error']['Code'], str(e))}"
    except Exception as e:
        return None, f"❌ Unexpected error in Secrets Manager: {e}"


@st.cache_data(ttl=600)
def load_data_from_s3(bucket_name, file_key, required_cols):
    """Downloads an Excel file from S3 and loads it into a Pandas DataFrame."""
    try:
        s3 = boto3.client('s3')
        obj = s3.get_object(Bucket=bucket_name, Key=file_key)
        excel_data = obj['Body'].read()
        df = pd.read_excel(BytesIO(excel_data))
        df.columns = df.columns.str.strip()
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            return None, f"❌ Missing essential columns: **{', '.join(missing)}**"
        df_filtered = df[required_cols]
        df_filtered['Annual Revenue'] = pd.to_numeric(df_filtered['Annual Revenue'], errors='coerce')
        return df_filtered, None
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            return None, f"❌ S3 File not found: s3://**{bucket_name}/{file_key}**"
        return None, f"❌ S3 Error: {e}"
    except Exception as e:
        return None, f"❌ Error reading/processing data: {e}"


def filter_data_context(df, query):
    """Filters the DataFrame based on keywords and returns a CSV string."""
    df_working = df.copy()
    query_lower = query.lower()
    key_phrases = ["best leads", "hot leads", "convertible", "potential", "possibility", "high value"]
    if any(p in query_lower for p in key_phrases):
        df_working = df_working[~df_working["Lead Status"].isin(DISQUALIFYING_STATUSES)]
    locations = ["bangalore", "bengaluru", "delhi", "new york", "london", "texas", "india"]
    loc_match = next((loc for loc in locations if loc in query_lower), None)
    if loc_match:
        mask = (
            df_working["City"].astype(str).str.lower().str.contains(loc_match, na=False) |
            df_working["State"].astype(str).str.lower().str.contains(loc_match, na=False) |
            df_working["Country"].astype(str).str.lower().str.contains(loc_match, na=False)
        )
        df_working = df_working[mask]
        if df_working.empty:
            df_working = df.head(0) 
    return df_working.to_csv(index=False, sep="\t")


def ask_gemini(question, data_context, api_key):
    """Sends the question and filtered data context to the Gemini API."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(GEMINI_MODEL) 
        prompt = f"""
You are ZODOPT Sales Buddy. You strictly analyze ONLY the following tab-separated CRM lead data.
Do not guess or hallucinate any values outside the dataset.
--- DATASET ---
{data_context}
--- QUESTION ---
{question}
Provide structured bullet-point insights, using the data fields provided.
"""
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        if "has no attribute 'Client'" in str(e):
            return "❌ Gemini API Configuration Error: The installed SDK version is too old. Please try updating it (`pip install --upgrade google-generativeai`)."
        return f"❌ Gemini API Error: {e}"

def get_initial(name):
    """Gets the first initial of a company name for the avatar."""
    cleaned_name = re.sub(r'[^a-zA-Z\s]', '', str(name)).strip()
    return cleaned_name[0].upper() if cleaned_name else '?'


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
    
    # --- 2. CUSTOM HEADER (Always Visible) ---
    st.markdown("""
        <div class='salesbuddy-header'>
            <div class='salesbuddy-header-left'>
                <span class='profile-icon'>👤</span>
                <div>
                    <div class='header-title'>SalesBuddy</div>
                    <div class='header-subtitle'>""" + user_data.get("full_name", "User") + """</div>
                </div>
            </div>
            <span class='search-icon'>🔎</span>
        </div>
    """, unsafe_allow_html=True)
    
    # API Credits display
    st.markdown("Total API Credits left **2,840**", unsafe_allow_html=True)

    
    # --- 3. LOGIC FOR VIEW SWITCHING ---
    if st.session_state.chat_initiated:
        
        # --- ACTIVE CHAT VIEW ---
        
        st.markdown("<div class='back-to-chat'>⬅️ Current Chat</div>", unsafe_allow_html=True)

        # Chat History Display Area
        st.markdown("<div class='chat-history-container'>", unsafe_allow_html=True)
        for msg in st.session_state.chat:
            if msg["role"] == "user":
                st.markdown(f"<div class='chat-bubble-user'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-bubble-ai'>{msg['content']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # --- Persistent Chat Input at the Bottom ---
        query = st.text_input("Ask your CRM-related question...", key="active_chat_input", label_visibility="collapsed")
        
        if query:
            st.session_state.chat.append({"role": "user", "content": query})
            
            with st.spinner("Analyzing..."):
                data_ctx = filter_data_context(df_filtered, query)
                reply = ask_gemini(query, data_ctx, gemini_api_key)
                st.session_state.chat.append({"role": "ai", "content": reply})
            
            # Use st.rerun() to redraw the history with the new message
            st.rerun()


    else:
        
        # --- NEW CHAT (START SCREEN) VIEW (Mimics Image) ---
        st.markdown("<div class='back-to-chat'>⬅️ New Chat</div>", unsafe_allow_html=True)

        # Input and Start Chat Button
        with st.form(key='new_chat_form'):
            search_query = st.text_input("", 
                placeholder="Enter company or person's name...", 
                key="new_chat_search_input", 
                label_visibility="collapsed")
            
            # Apply the custom input bar class using a hack 
            st.markdown(f"""
                <script>
                // Target the input within this form
                var input = window.parent.document.querySelector('[data-testid="stForm"] input[placeholder="Enter company or person\'s name..."]');
                if (input) {{
                    var parentDiv = input.closest('[data-testid="stTextInput"]');
                    if (parentDiv) {{
                        parentDiv.classList.add('centered-input-bar');
                    }}
                }}
                </script>
            """, unsafe_allow_html=True)
            
            submitted = st.form_submit_button("Start Chat", use_container_width=True)

            if submitted and search_query:
                # Clear existing chat history if starting a new, focused conversation
                st.session_state.chat = []
                st.session_state.chat_initiated = True
                
                # Treat the search query as the first question
                first_question = f"Analyze data for {search_query}."
                st.session_state.chat.append({"role": "user", "content": first_question})
                
                with st.spinner("Analyzing..."):
                    data_ctx = filter_data_context(df_filtered, search_query)
                    reply = ask_gemini(first_question, data_ctx, gemini_api_key)
                    st.session_state.chat.append({"role": "ai", "content": reply})
                    
                st.rerun()

        # Suggested Contacts
        st.markdown("### Suggested Contacts")
        top_contacts = df_filtered['Company'].dropna().unique()
        
        for i, contact_name in enumerate(top_contacts[:5]):
            initial = get_initial(contact_name)
            
            # Use a container hack for clickable styling
            contact_clicked = st.button(contact_name, key=f"contact_{i}", use_container_width=True)
            
            # Manually inject the styled content into the button container
            st.markdown(f"""
                <script>
                    var button = window.parent.document.getElementById('contact_{i}');
                    if (button) {{
                        var parentDiv = button.closest('[data-testid="stButton"]');
                        if (parentDiv) {{
                            parentDiv.innerHTML = `
                                <div class='suggested-contact-item'>
                                    <div class='contact-avatar'>{initial}</div>
                                    <div class='contact-name'>{contact_name}</div>
                                </div>
                            `;
                        }}
                    }}
                </script>
            """, unsafe_allow_html=True)
            
            if contact_clicked:
                st.session_state.chat = []
                st.session_state.chat_initiated = True
                
                first_question = f"Tell me all available details about {contact_name}."
                st.session_state.chat.append({"role": "user", "content": first_question})
                
                with st.spinner(f"Analyzing {contact_name}..."):
                    data_ctx = filter_data_context(df_filtered, contact_name)
                    reply = ask_gemini(first_question, data_ctx, gemini_api_key)
                    st.session_state.chat.append({"role": "ai", "content": reply})
                st.rerun()

    # --- Footer/Logout (Optional but good practice) ---
    st.markdown("<br><br><br><br>", unsafe_allow_html=True) # Spacer for fixed input bar
    if st.session_state.chat_initiated and st.button("End Chat / New Search"):
        st.session_state.chat_initiated = False
        st.session_state.chat = []
        st.rerun()
