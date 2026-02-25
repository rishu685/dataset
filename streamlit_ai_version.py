"""
Streamlit app with Google Gemini AI integration for Titanic Dataset Analysis
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
from typing import Dict, Any, Optional
import google.generativeai as genai

# Page configuration
st.set_page_config(
    page_title="🚢 Titanic Dataset Chat Agent",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
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
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_titanic_data():
    """Load the Titanic dataset."""
    try:
        url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
        df = pd.read_csv(url)
        return df
    except:
        st.error("Could not load Titanic dataset. Please check your internet connection.")
        return pd.DataFrame()

@st.cache_data
def get_basic_stats(df):
    """Get basic statistics about the dataset."""
    if df.empty:
        return {}
    
    return {
        "total_passengers": len(df),
        "survivors": df['Survived'].sum(),
        "survival_rate": df['Survived'].mean() * 100,
        "male_passengers": (df['Sex'] == 'male').sum(),
        "female_passengers": (df['Sex'] == 'female').sum(),
        "average_age": df['Age'].mean(),
        "average_fare": df['Fare'].mean(),
    }

def create_survival_chart(df):
    """Create survival rate by gender chart."""
    survival_data = df.groupby('Sex')['Survived'].mean() * 100
    
    fig = px.bar(
        x=['Female', 'Male'], 
        y=[survival_data['female'], survival_data['male']],
        title="Survival Rate by Gender",
        labels={'x': 'Gender', 'y': 'Survival Rate (%)'},
        color=['Female', 'Male'],
        color_discrete_map={'Female': '#E91E63', 'Male': '#2196F3'}
    )
    return fig

def create_age_histogram(df):
    """Create age distribution histogram."""
    fig = px.histogram(
        df, 
        x='Age',
        nbins=20,
        title="Age Distribution of Titanic Passengers",
        labels={'Age': 'Age', 'count': 'Count'}
    )
    return fig

def create_class_chart(df):
    """Create survival by class chart."""
    survival_rate = df.groupby('Pclass')['Survived'].mean() * 100
    
    fig = px.bar(
        x=['1st Class', '2nd Class', '3rd Class'],
        y=survival_rate.values,
        title="Survival Rate by Passenger Class",
        labels={'x': 'Passenger Class', 'y': 'Survival Rate (%)'},
        color_discrete_sequence=['#2E86AB', '#A23B72', '#F18F01']
    )
    return fig

@st.cache_resource
def setup_gemini():
    """Setup Google Gemini AI."""
    try:
        api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return None
        
        genai.configure(api_key=api_key)
        
        # Try current model names
        models_to_try = ['gemini-1.5-flash-latest', 'gemini-1.5-pro-latest', 'gemini-1.0-pro']
        
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                # Test the model with a simple request
                test_response = model.generate_content("Test")
                return model
            except:
                continue
        
        return None
    except:
        return None

def get_ai_response(question, df, model):
    """Get AI response using Gemini."""
    if not model:
        # Fallback to basic analysis when AI is not available
        return get_fallback_response(question, df), get_chart_for_question(question, df)
    
    try:
        # Create data summary
        stats = get_basic_stats(df)
        data_summary = f"""
        Titanic Dataset Summary:
        - Total passengers: {stats['total_passengers']}
        - Survivors: {stats['survivors']} ({stats['survival_rate']:.1f}%)
        - Average age: {stats['average_age']:.1f} years
        - Gender distribution: {stats['male_passengers']} males, {stats['female_passengers']} females
        """
        
        prompt = f"""
        You are a data analyst expert helping users understand the Titanic dataset.
        
        Dataset Information:
        {data_summary}
        
        User Question: {question}
        
        Provide a friendly, informative response about the Titanic dataset. If the question relates to:
        - Gender: Mention survival rates and create a gender chart
        - Age: Discuss age distribution and create an age histogram  
        - Class: Explain class survival differences and create a class chart
        - General stats: Provide overview information
        
        Keep responses concise but informative. Always mention relevant statistics.
        """
        
        response = model.generate_content(prompt)
        chart = get_chart_for_question(question, df)
        
        return response.text, chart
        
    except Exception as e:
        st.error(f"AI temporarily unavailable: {str(e)[:100]}")
        # Fallback to basic analysis
        return get_fallback_response(question, df), get_chart_for_question(question, df)

def get_fallback_response(question, df):
    """Fallback analysis when AI is not available."""
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['alive', 'total', 'how many']):
        total = len(df)
        survivors = df['Survived'].sum()
        return f"📊 **{survivors} passengers survived out of {total} total passengers** ({survivors/total*100:.1f}% survival rate). The tragedy claimed {total-survivors} lives."
    
    elif any(word in question_lower for word in ['gender', 'male', 'female', 'men', 'women']):
        stats = df.groupby('Sex')['Survived'].agg(['count', 'sum', 'mean'])
        male_survival = stats.loc['male', 'mean'] * 100
        female_survival = stats.loc['female', 'mean'] * 100
        
        return f"👨‍👩‍👧‍👦 **Gender played a crucial role in survival**: Women had a {female_survival:.1f}% survival rate, while men had only {male_survival:.1f}%. This reflects the 'women and children first' evacuation protocol."
    
    elif any(word in question_lower for word in ['age', 'young', 'old']):
        avg_age = df['Age'].mean()
        return f"📈 **Age distribution**: The average passenger age was {avg_age:.1f} years, ranging from {df['Age'].min():.0f} to {df['Age'].max():.0f} years. Age influenced survival chances significantly."
    
    elif any(word in question_lower for word in ['class', 'first', 'second', 'third']):
        class_survival = df.groupby('Pclass')['Survived'].mean() * 100
        return f"🎫 **Social class strongly influenced survival**: 1st class passengers had {class_survival[1]:.1f}% survival rate, 2nd class {class_survival[2]:.1f}%, and 3rd class {class_survival[3]:.1f}%."
    
    else:
        stats = get_basic_stats(df)
        return f"🚢 **Titanic Overview**: {stats['total_passengers']} passengers, {stats['survival_rate']:.1f}% survival rate. Try asking about survival by gender, age, or passenger class for detailed insights!"

def get_chart_for_question(question, df):
    """Get appropriate chart based on question."""
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['gender', 'male', 'female', 'men', 'women']):
        return create_survival_chart(df)
    elif any(word in question_lower for word in ['age', 'young', 'old']):
        return create_age_histogram(df)
    elif any(word in question_lower for word in ['class', 'first', 'second', 'third']):
        return create_class_chart(df)
    
    return None

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Load data and setup AI
df = load_titanic_data()
model = setup_gemini()

# Main header
st.markdown('<h1 class="main-header">🚢 AI-Powered Titanic Analysis</h1>', unsafe_allow_html=True)

# AI Status indicator
if model:
    st.success("🤖 AI Assistant is ready!")
else:
    st.info("📊 **Analysis Mode Active** - Your app is fully functional! For AI chat, get a fresh Google API key (current one may be expired) and add it to Secrets.")

# Sidebar
with st.sidebar:
    st.header("📊 Dataset Overview")
    if not df.empty:
        stats = get_basic_stats(df)
        st.metric("Total Passengers", f"{stats['total_passengers']:,}")
        st.metric("Survival Rate", f"{stats['survival_rate']:.1f}%")
        st.metric("Average Age", f"{stats['average_age']:.1f} years")
    
    st.header("💡 Try asking:")
    st.write("• What factors influenced survival?")
    st.write("• How did gender affect survival chances?")
    st.write("• Tell me about the age distribution")
    st.write("• Which passenger class had the best survival rate?")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 AI Chat Assistant")
    
    if not df.empty:
        user_question = st.text_area(
            "Ask anything about the Titanic dataset:",
            placeholder="e.g., What can you tell me about survival patterns?",
            height=100
        )
        
        if st.button("🚀 Ask AI", type="primary"):
            if user_question.strip():
                # Add to chat history
                st.session_state.chat_history.append({
                    "type": "user",
                    "content": user_question
                })
                
                # Get AI response
                with st.spinner("🤖 AI is analyzing..."):
                    answer, chart = get_ai_response(user_question, df, model)
                
                st.session_state.chat_history.append({
                    "type": "bot", 
                    "content": answer,
                    "chart": chart
                })
                st.rerun()
    else:
        st.error("Dataset not available. Please check your internet connection.")

with col2:
    st.header("📈 Visualization")
    chart_placeholder = st.empty()

# Display chat history
if st.session_state.chat_history:
    st.header("💬 Chat History")
    
    for i, message in enumerate(st.session_state.chat_history):
        if message["type"] == "user":
            st.markdown(
                f'<div class="user-message"><strong>You:</strong> {message["content"]}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="bot-message"><strong>🤖 AI:</strong> {message["content"]}</div>',
                unsafe_allow_html=True
            )
            
            # Display chart if available
            if message.get("chart"):
                with col2:
                    chart_placeholder.plotly_chart(message["chart"], use_container_width=True)

# Quick actions
if not df.empty:
    st.header("🚀 Quick AI Analysis")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👨‍👩‍👧‍👦 Gender Insights"):
            with st.spinner("🤖 Analyzing..."):
                answer, chart = get_ai_response("How did gender affect survival on the Titanic?", df, model)
            st.session_state.chat_history.extend([
                {"type": "user", "content": "How did gender affect survival on the Titanic?"},
                {"type": "bot", "content": answer, "chart": chart}
            ])
            st.rerun()
    
    with col2:
        if st.button("📊 Age Analysis"):
            with st.spinner("🤖 Analyzing..."):
                answer, chart = get_ai_response("What does the age distribution tell us about the passengers?", df, model)
            st.session_state.chat_history.extend([
                {"type": "user", "content": "What does the age distribution tell us about the passengers?"},
                {"type": "bot", "content": answer, "chart": chart}
            ])
            st.rerun()
    
    with col3:
        if st.button("🎫 Class Impact"):
            with st.spinner("🤖 Analyzing..."):
                answer, chart = get_ai_response("How did passenger class influence survival rates?", df, model)
            st.session_state.chat_history.extend([
                {"type": "user", "content": "How did passenger class influence survival rates?"},
                {"type": "bot", "content": answer, "chart": chart}
            ])
            st.rerun()

# Clear history
if st.session_state.chat_history:
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

# Footer
st.markdown("---")
st.markdown("🤖 **Powered by Google Gemini AI** | Built with ❤️ using Streamlit and Plotly")