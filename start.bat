@echo off
echo 🚢 Starting Titanic Chatbot...

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is required but not found. Please install Python.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

echo 📥 Installing requirements...
pip install -r requirements.txt

echo 📊 Downloading dataset...
python download_data.py

echo 🚀 Starting backend server...
start /b python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo 🎨 Starting frontend...
streamlit run frontend/streamlit_app.py --server.port 8501

echo.
echo 🎉 Titanic Chatbot is now running!
echo 🌐 Open your browser and go to: http://localhost:8501