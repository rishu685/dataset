"""
Standalone Streamlit app for Titanic Dataset Analysis
This version runs without the FastAPI backend for easier deployment
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
import os
from typing import Dict, Any, Optional

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
        # Try to load from URL
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
        "male_percentage": (df['Sex'] == 'male').mean() * 100,
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

def analyze_question(df, question):
    """Simple analysis based on question keywords."""
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['gender', 'male', 'female']):
        stats = df.groupby('Sex')['Survived'].agg(['count', 'sum', 'mean'])
        male_survival = stats.loc['male', 'mean'] * 100
        female_survival = stats.loc['female', 'mean'] * 100
        
        return f"Female passengers had a {female_survival:.1f}% survival rate, while male passengers had a {male_survival:.1f}% survival rate. Women were much more likely to survive the disaster.", create_survival_chart(df)
    
    elif any(word in question_lower for word in ['age', 'young', 'old']):
        avg_age = df['Age'].mean()
        return f"The average age of passengers was {avg_age:.1f} years. Ages ranged from {df['Age'].min():.0f} to {df['Age'].max():.0f} years.", create_age_histogram(df)
    
    elif any(word in question_lower for word in ['class', 'first', 'second', 'third']):
        class_survival = df.groupby('Pclass')['Survived'].mean() * 100
        return f"Passenger class strongly influenced survival: 1st class ({class_survival[1]:.1f}%), 2nd class ({class_survival[2]:.1f}%), 3rd class ({class_survival[3]:.1f}%).", create_class_chart(df)
    
    elif 'total' in question_lower or 'how many' in question_lower:
        total = len(df)
        survivors = df['Survived'].sum()
        return f"There were {total} passengers on the Titanic. {survivors} passengers survived ({survivors/total*100:.1f}% survival rate).", None
    
    else:
        stats = get_basic_stats(df)
        return f"The Titanic had {stats['total_passengers']} passengers with a {stats['survival_rate']:.1f}% survival rate. Try asking about survival by gender, age, or passenger class!", None

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Load data
df = load_titanic_data()

# Main header
st.markdown('<h1 class="main-header">🚢 Titanic Dataset Analysis</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📊 Dataset Overview")
    if not df.empty:
        stats = get_basic_stats(df)
        st.metric("Total Passengers", f"{stats['total_passengers']:,}")
        st.metric("Survival Rate", f"{stats['survival_rate']:.1f}%")
        st.metric("Average Age", f"{stats['average_age']:.1f} years")
    
    st.header("💡 Try asking:")
    st.write("• What was the survival rate by gender?")
    st.write("• Show me the age distribution")
    st.write("• How did passenger class affect survival?")
    st.write("• How many passengers were there?")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Ask About the Data")
    
    if not df.empty:
        user_question = st.text_area(
            "Ask a question about the Titanic dataset:",
            placeholder="e.g., What was the survival rate for women?",
            height=100
        )
        
        if st.button("🚀 Analyze", type="primary"):
            if user_question.strip():
                # Add to chat history
                st.session_state.chat_history.append({
                    "type": "user",
                    "content": user_question
                })
                
                # Get analysis
                answer, chart = analyze_question(df, user_question)
                
                st.session_state.chat_history.append({
                    "type": "bot", 
                    "content": answer,
                    "chart": chart
                })
    else:
        st.error("Dataset not available. Please check your internet connection.")

with col2:
    st.header("📈 Visualization")
    # Chart display area
    chart_placeholder = st.empty()

# Display chat history
if st.session_state.chat_history:
    st.header("💬 Analysis History")
    
    for message in st.session_state.chat_history:
        if message["type"] == "user":
            st.markdown(
                f'<div class="user-message"><strong>You:</strong> {message["content"]}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="bot-message"><strong>🤖 Analysis:</strong> {message["content"]}</div>',
                unsafe_allow_html=True
            )
            
            # Display chart if available
            if message.get("chart"):
                with col2:
                    chart_placeholder.plotly_chart(message["chart"], use_container_width=True)

# Quick actions
if not df.empty:
    st.header("🚀 Quick Analysis")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👨‍👩‍👧‍👦 Gender Analysis"):
            answer, chart = analyze_question(df, "survival by gender")
            st.session_state.chat_history.extend([
                {"type": "user", "content": "Analyze survival by gender"},
                {"type": "bot", "content": answer, "chart": chart}
            ])
            st.rerun()
    
    with col2:
        if st.button("📊 Age Distribution"):
            answer, chart = analyze_question(df, "age distribution")
            st.session_state.chat_history.extend([
                {"type": "user", "content": "Show age distribution"},
                {"type": "bot", "content": answer, "chart": chart}
            ])
            st.rerun()
    
    with col3:
        if st.button("🎫 Class Analysis"):
            answer, chart = analyze_question(df, "survival by class")
            st.session_state.chat_history.extend([
                {"type": "user", "content": "Analyze survival by passenger class"},
                {"type": "bot", "content": answer, "chart": chart}
            ])
            st.rerun()

# Clear history
if st.session_state.chat_history:
    if st.button("🗑️ Clear History"):
        st.session_state.chat_history = []
        st.rerun()

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and Plotly")