# Titanic Dataset Chat Agent 🚢

A friendly chatbot that analyzes the famous Titanic dataset using natural language queries. Built with FastAPI, LangChain, and Streamlit.

## Features 🌟

- **AI-Powered Analysis**: Google Gemini AI for intelligent responses
- **Natural Language Queries**: Ask complex questions in plain English
- **Visual Insights**: Automatic charts and graphs
- **Interactive Interface**: Clean and intuitive Streamlit frontend
- **Fast API Backend**: RESTful API with FastAPI
- **Smart Visualizations**: Context-aware chart generation

## Example Questions 🤔

**AI-Enhanced Queries:**
- "What factors influenced survival on the Titanic?"
- "Compare survival rates between different passenger classes and explain why"
- "Show me interesting patterns in the age distribution"
- "What can you tell me about the relationship between fare prices and survival?"
- "Analyze the embarkation data and its impact on survival"
- "What demographic had the best survival chances and why?"

**Quick Data Queries:**
- "What percentage of passengers were male on the Titanic?"
- "Show me a histogram of passenger ages"
- "What was the average ticket fare?"
- "How many passengers embarked from each port?"

## Setup Instructions 🛠️

1. **Get Gemini API Key** (Free!):
   - Go to https://ai.google.dev/
   - Get your free API key
   - Either set as environment variable: `export GEMINI_API_KEY="your-key"`
   - Or enter it in the Streamlit sidebar when the app starts

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Quick Start** (Automated):
   ```bash
   ./start.sh  # On macOS/Linux
   # OR
   start.bat   # On Windows
   ```

4. **Manual Start**:
   ```bash
   # Start Backend
   python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
   
   # Start Frontend (new terminal)
   streamlit run frontend/streamlit_app.py --server.port 8501
   ```

5. **Open in Browser**:
   Navigate to `http://localhost:8501`

## Project Structure 📁

```
titanic-chatbot/
├── requirements.txt          # Python dependencies
├── config.py                # Configuration settings
├── data/                    # Dataset storage
│   └── titanic.csv         # Titanic dataset
├── backend/                # FastAPI backend
│   ├── main.py            # FastAPI application
│   ├── models.py          # Pydantic models
│   ├── agent.py           # LangChain agent
│   └── data_analyzer.py   # Data analysis functions
└── frontend/              # Streamlit frontend
    └── streamlit_app.py   # Main Streamlit interface
```

## Tech Stack 🔧

- **AI**: Google Gemini 1.5 Flash
- **Backend**: FastAPI + LangChain
- **Frontend**: Streamlit
- **Data Analysis**: Pandas, NumPy
- **Visualizations**: Matplotlib, Seaborn, Plotly
- **AI Framework**: LangChain with Google GenAI

## Usage Examples 📝

The chatbot can answer various types of questions:

1. **Basic Statistics**: "How many passengers were on the Titanic?"
2. **Demographics**: "Show me the age distribution of passengers"
3. **Survival Analysis**: "What was the survival rate by gender?"
4. **Visualizations**: "Create a chart showing ticket prices by class"

## Development 👩‍💻

To extend the chatbot:

1. Add new analysis functions in `backend/data_analyzer.py`
2. Update the LangChain agent prompts in `backend/agent.py`
3. Enhance the UI in `frontend/streamlit_app.py`