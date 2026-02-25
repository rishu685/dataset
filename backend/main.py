"""
FastAPI backend for Titanic chatbot
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.models import ChatRequest, ChatResponse, HealthResponse
from backend.agent import TitanicAgent
from backend.data_analyzer import TitanicAnalyzer

# Initialize FastAPI app
app = FastAPI(
    title="Titanic Chatbot API",
    description="AI-powered chatbot for analyzing the Titanic dataset",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent
agent = TitanicAgent()
analyzer = TitanicAnalyzer()

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="Titanic Chatbot API is running",
        dataset_loaded=not analyzer.df.empty
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check."""
    return HealthResponse(
        status="healthy" if not analyzer.df.empty else "warning",
        message="API is running" if not analyzer.df.empty else "Dataset not loaded",
        dataset_loaded=not analyzer.df.empty
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint for processing user questions."""
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Process the question using the agent
        response = agent.process_query(request.question)
        
        return ChatResponse(
            answer=response["answer"],
            data=response.get("data"),
            chart_html=response.get("chart_html"),
            chart_type=response.get("chart_type")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.get("/dataset/stats")
async def get_dataset_stats():
    """Get basic dataset statistics."""
    try:
        stats = analyzer.get_basic_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@app.get("/dataset/survival/gender")
async def get_survival_by_gender():
    """Get survival statistics by gender."""
    try:
        return analyzer.get_survival_by_gender()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting gender stats: {str(e)}")

@app.get("/dataset/survival/class")
async def get_survival_by_class():
    """Get survival statistics by passenger class."""
    try:
        return analyzer.get_survival_by_class()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting class stats: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)