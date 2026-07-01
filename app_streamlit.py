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

# ===== CUSTOM CSS FOR SHL THEME =====
st.markdown("""
<style>
    :root {
        --primary-dark: #003D2E;
        --primary-medium: #2B9B6E;
        --primary-light: #00FF7F;
        --secondary-light: #F5F5F5;
        --accent-white: #FFFFFF;
        --text-dark: #1A1A1A;
    }
    
    .stApp {
        background: linear-gradient(135deg, var(--secondary-light) 0%, var(--accent-white) 100%);
    }
    
    .header-container {
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary-medium) 100%);
        padding: 40px;
        border-radius: 15px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 8px 16px rgba(0, 61, 46, 0.15);
    }
    
    .header-title {
        font-size: 2.8em;
        font-weight: 700;
        margin: 0;
        color: var(--accent-white);
    }
    
    .header-subtitle {
        font-size: 1.15em;
        margin-top: 12px;
        color: rgba(255, 255, 255, 0.92);
    }
    
    .chat-user {
        background: linear-gradient(135deg, var(--primary-medium) 0%, var(--primary-dark) 100%);
        color: white;
        padding: 16px 22px;
        border-radius: 12px;
        margin: 12px 0;
        border-left: 5px solid var(--primary-light);
    }
    
    .chat-bot {
        background: linear-gradient(135deg, var(--accent-white) 0%, var(--secondary-light) 100%);
        color: var(--text-dark);
        padding: 16px 22px;
        border-radius: 12px;
        margin: 12px 0;
        border-left: 5px solid var(--primary-medium);
    }
    
    .recommendation-card {
        background: linear-gradient(135deg, var(--accent-white) 0%, var(--secondary-light) 100%);
        border-left: 6px solid var(--primary-light);
        padding: 18px;
        margin: 12px 0;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 61, 46, 0.1);
    }
    
    .recommendation-name {
        font-weight: 700;
        color: var(--primary-dark);
        font-size: 1.08em;
        display: block;
        margin-bottom: 8px;
    }
    
    .recommendation-type {
        color: #666666;
        font-size: 0.92em;
        display: block;
        margin-bottom: 8px;
        font-weight: 500;
    }
    
    .recommendation-link {
        color: var(--primary-medium);
        text-decoration: none;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ===== HEADER =====
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title"> SHL Assessment Recommender</h1>
        <p class="header-subtitle">Find the Perfect Assessment for Your Hiring Needs</p>
    </div>
    """, unsafe_allow_html=True)

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: rgba(0, 61, 46, 0.1); border-radius: 12px; margin-bottom: 20px;">
        <h3 style="color: #003D2E; margin-top: 0;"> How to Use</h3>
        <p style="color: #666; font-size: 0.95em;">
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
    <div style="background: rgba(0, 61, 46, 0.1); padding: 15px; border-radius: 8px;">
        <h4 style="color: #003D2E;">Aa About This Bot</h4>
        <p style="font-size: 0.9em; margin-bottom: 0; color: #666;">
            This is an AI-powered chatbot that helps hiring managers find the perfect SHL assessments through natural conversation.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ===== INITIALIZE SESSION STATE =====
if "messages" not in st.session_state:
    st.session_state.messages = []

# ===== DISPLAY CHAT HISTORY =====
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
            <strong> Bot:</strong> {msg['content']}
        </div>
        """, unsafe_allow_html=True)
        
        # Show recommendations if they exist
        if "recommendations" in msg and msg["recommendations"]:
            st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #003D2E;'> Recommended Assessments:</h4>", unsafe_allow_html=True)
            
            for i, rec in enumerate(msg["recommendations"], 1):
                st.markdown(f"""
                <div class="recommendation-card">
                    <span class="recommendation-name">{i}. {rec['name']}</span>
                    <span class="recommendation-type">Type: {rec['test_type']}</span>
                    <a href="{rec['url']}" target="_blank" class="recommendation-link">🔗 View Assessment →</a>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)

# ===== CHAT INPUT =====
user_input = st.chat_input(
    "Ask me about SHL assessments... (e.g., 'I need a test for Python developers')",
    key="chat_input"
)

if user_input:
    # Add user message to session state
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Call API
    try:
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
            
            # Add bot message to session state
            st.session_state.messages.append({
                "role": "assistant",
                "content": bot_response["reply"],
                "recommendations": bot_response.get("recommendations", []),
                "end_of_conversation": bot_response.get("end_of_conversation", False)
            })
            
            # Success message
            if bot_response.get("end_of_conversation"):
                st.success("Conversation Complete! Good luck with your hiring!")
        
        else:
            st.error(f"API Error: {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to API. Make sure `python api.py` is running in another terminal.")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Display chat history (this refreshes automatically when messages change)
with st.container():
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
                <strong> Bot:</strong> {msg['content']}
            </div>
            """, unsafe_allow_html=True)
            
            # Show recommendations if they exist
            if "recommendations" in msg and msg["recommendations"]:
                st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
                st.markdown("<h4 style='color: var(--primary-dark);'> Recommended Assessments:</h4>", unsafe_allow_html=True)
                
                for i, rec in enumerate(msg["recommendations"], 1):
                    st.markdown(f"""
                    <div class="recommendation-card">
                        <span class="recommendation-name">{i}. {rec['name']}</span>
                        <span class="recommendation-type">Type: {rec['test_type']}</span>
                        <a href="{rec['url']}" target="_blank" class="recommendation-link">View Assessment →</a>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<div class='divider'></div>", unsafe_allow_html=True)