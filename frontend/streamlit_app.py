"""
Streamlit frontend for Titanic chatbot
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from typing import Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import BACKEND_URL

# Page configuration
st.set_page_config(
    page_title="🚢 Titanic Dataset Chat Agent",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-container {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        background-color: #f9f9f9;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        color: #1565c0;
        font-weight: 500;
    }
    .bot-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        color: #6a1b9a;
        font-weight: 400;
        line-height: 1.6;
    }
    .user-label {
        font-weight: bold;
        color: #1976d2;
        margin-bottom: 5px;
    }
    .bot-label {
        font-weight: bold;
        color: #7b1fa2;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

def check_backend_health():
    """Check if backend is running."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def send_chat_request(question: str) -> Dict[str, Any]:
    """Send question to backend API.""" 
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={"question": question},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error {response.status_code}: {response.text}"}
    except requests.exceptions.ConnectionError:
        return {"error": "Connection failed. Make sure the backend server is running at http://127.0.0.1:8000"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. The server might be busy processing your request."}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def get_dataset_stats():
    """Get basic dataset statistics."""
    try:
        response = requests.get(f"{BACKEND_URL}/dataset/stats", timeout=10)
        if response.status_code == 200:
            return response.json()
        return {}
    except:
        return {}

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'message_counter' not in st.session_state:
    st.session_state.message_counter = 0

# Main interface
st.markdown('<h1 class="main-header">🚢 Titanic Dataset Chat Agent (AI-Powered)</h1>', unsafe_allow_html=True)

# Sidebar with information
with st.sidebar:
    st.header("ℹ️ About")
    st.write("Ask questions about the Titanic dataset using natural language powered by Google Gemini AI!")
    
    # Backend status
    backend_status = check_backend_health()
    if backend_status:
        st.success("✅ Backend Connected")
    else:
        st.error("❌ Backend Offline")
        st.write("Make sure to start the backend server:")
        st.code("python -m uvicorn backend.main:app --reload")
    
    # Dataset stats
    if backend_status:
        st.header("📊 Dataset Overview")
        stats = get_dataset_stats()
        if stats and 'total_passengers' in stats:
            st.metric("Total Passengers", stats['total_passengers'])
            st.metric("Survival Rate", f"{stats['survival_rate']:.1f}%")
            st.metric("Average Age", f"{stats['average_age']:.1f} years")
    
    st.header("💡 Example Questions")
    st.write("**AI-Powered Examples:**")
    st.write("• What factors influenced survival on the Titanic?")
    st.write("• Compare survival rates between men and women")
    st.write("• Show me how passenger class affected survival")
    st.write("• What was the age distribution like?")
    st.write("• Tell me something interesting about the data")
    st.write("• How did embarkation port relate to survival?")

# Add welcome messages if chat is empty (after backend_status is defined)
if len(st.session_state.chat_history) == 0 and backend_status:
    st.session_state.message_counter += 1
    st.session_state.chat_history = [
        {
            "id": f"welcome_{st.session_state.message_counter}",
            "type": "bot", 
            "content": {
                "answer": "Welcome to the Titanic Dataset Chat Agent! 🚢 I'm powered by Google Gemini AI and ready to help you explore the famous Titanic passenger dataset. You can ask me questions about survival rates, demographics, passenger classes, ages, fares, and much more. I can also create visualizations to help illustrate the data. Try asking something like 'What factors influenced survival on the Titanic?' to get started!"
            }
        }
    ]

# Main chat interface
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Chat with the Dataset")
    
    # Chat input
    if backend_status:
        st.subheader("📝 Ask a Question")
        
        # Create a more prominent chat interface
        with st.container():
            user_question = st.text_area(
                "Ask a question about the Titanic dataset:",
                placeholder="e.g., What factors influenced survival on the Titanic?",
                height=100,
                key="user_input"
            )
            
            col_send, col_clear = st.columns([1, 4])
            with col_send:
                send_button = st.button("🚀 Send", type="primary", use_container_width=True)
        
        # Process the question
        if send_button and user_question.strip():
            # Prevent duplicate processing
            if st.session_state.get('last_processed_question') != user_question:
                st.session_state['last_processed_question'] = user_question
                st.session_state.message_counter += 1
                
                # Add user message to history with unique ID
                st.session_state.chat_history.append({
                    "id": f"user_{st.session_state.message_counter}",
                    "type": "user",
                    "content": user_question
                })
                
                # Get response from backend
                with st.spinner("🤖 AI is analyzing the data..."):
                    response = send_chat_request(user_question)
                
                st.session_state.message_counter += 1
                
                # Add bot response to history with unique ID
                st.session_state.chat_history.append({
                    "id": f"bot_{st.session_state.message_counter}",
                    "type": "bot",
                    "content": response
                })
                
                # Force refresh to show new messages
                st.rerun()
    else:
        st.error("⚠️ Please start the backend server to begin chatting.")
        st.code("python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000")

with col2:
    st.header("📈 Visualizations")
    visualization_placeholder = st.empty()

# Display chat history
if st.session_state.chat_history:
    st.header("💬 Conversation History")
    
    for i, message in enumerate(st.session_state.chat_history):
        # Use unique key for each message container
        message_key = message.get("id", f"msg_{i}")
        
        with st.container():
            if message["type"] == "user":
                # User message with better formatting
                st.markdown(
                    f"""
                    <div class="user-message">
                        <div class="user-label">You:</div>
                        <div style="color: #1565c0; font-size: 16px;">
                            {message["content"]}
                        </div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            else:
                # Bot message
                content = message["content"]
                if isinstance(content, dict):
                    if "error" in content:
                        st.error(f"Error: {content['error']}")
                    else:
                        answer_text = content.get("answer", "No answer provided")
                        st.markdown(
                            f"""
                            <div class="bot-message">
                                <div class="bot-label">🤖 AI Assistant:</div>
                                <div style="color: #6a1b9a; font-size: 16px; line-height: 1.6;">
                                    {answer_text}
                                </div>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                        
                        # Display chart if available
                        if content.get("chart_html"):
                            with col2:
                                with visualization_placeholder.container():
                                    st.components.v1.html(content["chart_html"], height=450)
                                    
                        # Show raw data if available (optional)
                        if content.get("data"):
                            with st.expander("📊 View Raw Data", expanded=False, key=f"data_{message_key}"):
                                st.json(content["data"])
                else:
                    # Fallback for string content
                    st.markdown(
                        f"""
                        <div class="bot-message">
                            <div class="bot-label">🤖 AI Assistant:</div>
                            <div style="color: #6a1b9a; font-size: 16px;">
                                {content}
                            </div>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )

# Quick action buttons
if backend_status:
    st.header("🚀 AI-Powered Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🧠 AI Analysis"):
            question = "What are the most interesting insights about survival on the Titanic?"
            if st.session_state.get('last_quick_action') != question:
                st.session_state['last_quick_action'] = question
                st.session_state.message_counter += 1
                st.session_state.chat_history.append({"id": f"user_{st.session_state.message_counter}", "type": "user", "content": question})
                response = send_chat_request(question)
                st.session_state.message_counter += 1
                st.session_state.chat_history.append({"id": f"bot_{st.session_state.message_counter}", "type": "bot", "content": response})
                st.rerun()
    
    with col2:
        if st.button("👨‍👩‍👧‍👦 Gender Insights"):
            question = "Analyze and compare survival rates between men and women with explanations"
            if st.session_state.get('last_quick_action') != question:
                st.session_state['last_quick_action'] = question
                st.session_state.message_counter += 1
                st.session_state.chat_history.append({"id": f"user_{st.session_state.message_counter}", "type": "user", "content": question})
                response = send_chat_request(question)
                st.session_state.message_counter += 1
                st.session_state.chat_history.append({"id": f"bot_{st.session_state.message_counter}", "type": "bot", "content": response})
                st.rerun()
    
    with col3:
        if st.button("🎫 Class Impact"):
            question = "Show me how passenger class affected survival chances with a chart"
            if st.session_state.get('last_quick_action') != question:
                st.session_state['last_quick_action'] = question
                st.session_state.message_counter += 1
                st.session_state.chat_history.append({"id": f"user_{st.session_state.message_counter}", "type": "user", "content": question})
                response = send_chat_request(question)
                st.session_state.message_counter += 1
                st.session_state.chat_history.append({"id": f"bot_{st.session_state.message_counter}", "type": "bot", "content": response})
                st.rerun()
    
    with col4:
        if st.button("📊 Age Demographics"):
            question = "Show me the age distribution and explain what it tells us about the passengers"
            if st.session_state.get('last_quick_action') != question:
                st.session_state['last_quick_action'] = question
                st.session_state.message_counter += 1
                st.session_state.chat_history.append({"id": f"user_{st.session_state.message_counter}", "type": "user", "content": question})
                response = send_chat_request(question)
                st.session_state.message_counter += 1
                st.session_state.chat_history.append({"id": f"bot_{st.session_state.message_counter}", "type": "bot", "content": response})
                st.rerun()

# Clear chat button
if st.session_state.chat_history:
    st.markdown("---")
    col_clear, col_space = st.columns([1, 3])
    with col_clear:
        if st.button("🗑️ Clear Chat History", type="secondary"):
            st.session_state.chat_history = []
            st.session_state.message_counter = 0
            st.session_state.pop('last_processed_question', None)
            st.session_state.pop('last_quick_action', None)
            st.success("Chat history cleared!")
            st.rerun()

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using FastAPI, LangChain, Streamlit, and Google Gemini AI")