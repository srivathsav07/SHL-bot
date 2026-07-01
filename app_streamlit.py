import streamlit as st
import requests
import json
from datetime import datetime

# ===== PAGE CONFIG WITH SHL THEME =====
st.set_page_config(
    page_title="SHL Assessment Bot",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== CUSTOM CSS WITH COLOR PALETTE & ANIMATIONS =====
st.markdown("""
<style>
    /* Color Palette from Design System */
    :root {
        --primary-dark: #003D2E;      /* Rich Dark Green */
        --primary-medium: #2B9B6E;    /* Mountain Meadow */
        --primary-light: #00FF7F;     /* Caribbean Green */
        --secondary-dark: #0A0E27;    /* Anti-Flash White (dark) */
        --secondary-light: #F5F5F5;   /* Stone Gray */
        --accent-white: #FFFFFF;
        --text-dark: #1A1A1A;
        --text-light: #666666;
    }
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, var(--secondary-light) 0%, var(--accent-white) 100%);
    }
    
    /* Header styling with animation */
    .header-container {
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary-medium) 100%);
        padding: 40px;
        border-radius: 15px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 8px 16px rgba(0, 61, 46, 0.15);
        animation: slideDown 0.6s ease-out;
    }
    
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .header-title {
        font-size: 2.8em;
        font-weight: 700;
        margin: 0;
        color: var(--accent-white);
        letter-spacing: -0.5px;
    }
    
    .header-subtitle {
        font-size: 1.15em;
        margin-top: 12px;
        color: rgba(255, 255, 255, 0.92);
        font-weight: 400;
    }
    
    /* Chat message styling */
    .chat-user {
        background: linear-gradient(135deg, var(--primary-medium) 0%, var(--primary-dark) 100%);
        color: white;
        padding: 16px 22px;
        border-radius: 12px;
        margin: 12px 0;
        border-left: 5px solid var(--primary-light);
        box-shadow: 0 4px 12px rgba(43, 155, 110, 0.12);
        animation: slideInLeft 0.4s ease-out;
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .chat-bot {
        background: linear-gradient(135deg, var(--accent-white) 0%, var(--secondary-light) 100%);
        color: var(--text-dark);
        padding: 16px 22px;
        border-radius: 12px;
        margin: 12px 0;
        border-left: 5px solid var(--primary-medium);
        box-shadow: 0 4px 12px rgba(0, 61, 46, 0.08);
        animation: slideInRight 0.4s ease-out;
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Recommendation styling with hover animation */
    .recommendation-card {
        background: linear-gradient(135deg, var(--accent-white) 0%, var(--secondary-light) 100%);
        border-left: 6px solid var(--primary-light);
        padding: 18px;
        margin: 12px 0;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 61, 46, 0.1);
        transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        cursor: pointer;
    }
    
    .recommendation-card:hover {
        transform: translateX(8px) translateY(-2px);
        box-shadow: 0 8px 20px rgba(43, 155, 110, 0.18);
        border-left-color: var(--primary-medium);
    }
    
    .recommendation-name {
        font-weight: 700;
        color: var(--primary-dark);
        font-size: 1.08em;
        display: block;
        margin-bottom: 8px;
        transition: color 0.3s ease;
    }
    
    .recommendation-card:hover .recommendation-name {
        color: var(--primary-medium);
    }
    
    .recommendation-type {
        color: var(--text-light);
        font-size: 0.92em;
        display: block;
        margin-bottom: 8px;
        font-weight: 500;
    }
    
    .recommendation-link {
        color: var(--primary-medium);
        text-decoration: none;
        font-weight: 600;
        display: inline-block;
        transition: all 0.3s ease;
    }
    
    .recommendation-link:hover {
        color: var(--primary-dark);
        transform: translateX(4px);
    }
    
    /* Input styling */
    .stChatInput {
        border: 2px solid var(--primary-medium) !important;
        border-radius: 12px !important;
        background: var(--accent-white) !important;
    }
    
    .stChatInput:focus {
        border-color: var(--primary-light) !important;
        box-shadow: 0 0 0 3px rgba(43, 155, 110, 0.15) !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-medium) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 12px 32px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(43, 155, 110, 0.2) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 6px 16px rgba(43, 155, 110, 0.3) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) !important;
    }
    
    /* Divider */
    .divider {
        background: linear-gradient(90deg, transparent, var(--primary-medium), transparent);
        height: 2px;
        margin: 20px 0;
        animation: expandWidth 0.5s ease-out;
    }
    
    @keyframes expandWidth {
        from {
            width: 0;
        }
        to {
            width: 100%;
        }
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--primary-dark) 0%, var(--primary-medium) 100%);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    
    /* How to use box */
    .how-to-box {
        text-align: center;
        padding: 20px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        margin-bottom: 20px;
        border: 1px solid rgba(0, 255, 127, 0.2);
        animation: fadeIn 0.6s ease-out 0.2s both;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    .how-to-box h3 {
        color: white;
        margin-top: 0;
        margin-bottom: 12px;
        font-weight: 700;
    }
    
    .how-to-box p {
        color: rgba(255, 255, 255, 0.92);
        font-size: 0.95em;
        line-height: 1.6;
        margin: 0;
    }
    
    /* About box */
    .about-box {
        background: rgba(255, 255, 255, 0.1);
        padding: 16px;
        border-radius: 10px;
        color: white;
        border: 1px solid rgba(0, 255, 127, 0.2);
        animation: fadeIn 0.6s ease-out 0.3s both;
    }
    
    .about-box h4 {
        margin-top: 0;
        margin-bottom: 10px;
        font-weight: 700;
        color: var(--primary-light);
    }
    
    .about-box p {
        font-size: 0.9em;
        margin-bottom: 0;
        color: rgba(255, 255, 255, 0.92);
        line-height: 1.5;
    }
    
    /* Success message */
    .stSuccess {
        background: linear-gradient(135deg, rgba(0, 255, 127, 0.1) 0%, rgba(43, 155, 110, 0.1) 100%) !important;
        border-left: 4px solid var(--primary-light) !important;
        border-radius: 8px !important;
    }
    
    /* Error message */
    .stError {
        background: linear-gradient(135deg, rgba(220, 53, 69, 0.1) 0%, rgba(255, 107, 107, 0.1) 100%) !important;
        border-left: 4px solid #FF6B6B !important;
        border-radius: 8px !important;
    }
    
    /* Spinner animation */
    .stSpinner > div {
        border-top-color: var(--primary-medium) !important;
    }
    
    /* Footer */
    .footer-text {
        text-align: center;
        color: var(--text-light);
        font-size: 0.95em;
        padding: 20px;
    }
    
    .footer-text p {
        margin: 8px 0;
    }
    
    .api-status {
        color: var(--primary-light);
        font-weight: 600;
    }
    
    /* Metric card animation */
    [data-testid="metric-container"] {
        animation: fadeIn 0.6s ease-out 0.4s both;
    }
    
</style>
""", unsafe_allow_html=True)

# ===== HEADER =====
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title">Ff SHL Assessment Recommender</h1>
        <p class="header-subtitle">Find the Perfect Assessment for Your Hiring Needs</p>
    </div>
    """, unsafe_allow_html=True)

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown("""
    <div class="how-to-box">
        <h3>Ff How to Use</h3>
        <p>
            1️⃣ Describe the role you're hiring for<br>
            2️⃣ Answer my clarifying questions<br>
            3️⃣ I'll recommend 1–10 real SHL tests<br>
            4️⃣ Click the links to view details
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.session_state.get("messages"):
        turn_count = len([m for m in st.session_state.messages if m["role"] == "user"])
        st.metric("Conversation Turns", turn_count, "/ 8 max")
    
    st.markdown("---")
    
    st.markdown("""
    <div class="about-box">
        <h4>Aa About This Bot</h4>
        <p>
            This is an AI-powered chatbot that helps hiring managers find the perfect SHL assessments through natural conversation.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ===== INITIALIZE SESSION STATE =====
if "messages" not in st.session_state:
    st.session_state.messages = []

# ===== DISPLAY CHAT HISTORY =====
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="chat-user">
                <strong>Xx You:</strong> {msg['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-bot">
                <strong>Ff Bot:</strong> {msg['content']}
            </div>
            """, unsafe_allow_html=True)
            
            # Show recommendations if they exist
            if "recommendations" in msg and msg["recommendations"]:
                st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
                st.markdown("<h4 style='color: var(--primary-dark); font-weight: 700; margin-bottom: 16px;'>Ff Recommended Assessments:</h4>", unsafe_allow_html=True)
                
                for i, rec in enumerate(msg["recommendations"], 1):
                    st.markdown(f"""
                    <div class="recommendation-card">
                        <span class="recommendation-name">{i}. {rec['name']}</span>
                        <span class="recommendation-type">Type: {rec['test_type']}</span>
                        <a href="{rec['url']}" target="_blank" class="recommendation-link">View Assessment →</a>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ===== CHAT INPUT =====
user_input = st.chat_input(
    "Ask me about SHL assessments... (e.g., 'I need a test for Python developers')",
    key="chat_input"
)

if user_input:
    # Check if this is a new message (not already in session)
    if not st.session_state.messages or st.session_state.messages[-1]["role"] == "user":
        # Add user message only if last message was from bot (or no messages yet)
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Call API
        try:
            with st.spinner("Analyzing your request..."):
                response = requests.post(
                    "http://localhost:8000/chat",
                    json={
                        "messages": [
                            {
                                "role": m["role"],
                                "content": m["content"]
                            }
                            for m in st.session_state.messages
                        ]
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    bot_response = response.json()
                    
                    # Add bot message
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": bot_response["reply"],
                        "recommendations": bot_response.get("recommendations", []),
                        "end_of_conversation": bot_response.get("end_of_conversation", False)
                    })
                    
                    # Success message
                    if bot_response.get("end_of_conversation"):
                        st.success("Conversation Complete! Good luck with your hiring!")
                    
                    st.rerun()
                else:
                    st.error(f"API Error: {response.status_code}")
        
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to API. Make sure `python api.py` is running in another terminal.")
        except Exception as e:
            st.error(f"Error: {str(e)}")