"""
Configuration settings for Titanic Chatbot
"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
TITANIC_DATA_PATH = DATA_DIR / "titanic.csv"

# API settings
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8000
BACKEND_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"

# Streamlit settings
FRONTEND_HOST = "127.0.0.1"
FRONTEND_PORT = 8501

# AI API settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Gemini model configuration
GEMINI_MODEL = "models/gemini-2.5-flash"
GEMINI_TEMPERATURE = 0.1
GEMINI_MAX_TOKENS = 2048

# Dataset URL
TITANIC_DATA_URL = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"