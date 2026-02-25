#!/bin/bash

# Quick start script for Titanic Chatbot with Gemini AI
echo "🚢 Starting Titanic Chatbot with AI..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found. Please install Python 3."
    exit 1
fi

# Install requirements if they don't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "📥 Installing requirements..."
pip install -r requirements.txt

echo "📊 Downloading dataset..."
python download_data.py

echo ""
echo "🔑 IMPORTANT: Get your FREE Gemini API key at https://ai.google.dev/"
echo "   You can enter it in the Streamlit sidebar when the app starts."
echo ""

echo "🚀 Starting backend server..."
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

echo "⏳ Waiting for backend to start..."
sleep 5

echo "🎨 Starting frontend with AI capabilities..."
streamlit run frontend/streamlit_app.py --server.port 8501 &
FRONTEND_PID=$!

echo ""
echo "🎉 Titanic Chatbot is now running with AI!"
echo "🌐 Open your browser and go to: http://localhost:8501"
echo "🔑 Remember to add your Gemini API key in the sidebar for AI features"
echo ""
echo "To stop the application, press Ctrl+C"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped."
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM

# Wait for user to stop
wait