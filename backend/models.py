"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel
from typing import Dict, Any, Optional

class ChatRequest(BaseModel):
    question: str
    
class ChatResponse(BaseModel):
    answer: str
    data: Optional[Dict[str, Any]] = None
    chart_html: Optional[str] = None
    chart_type: Optional[str] = None
    
class HealthResponse(BaseModel):
    status: str
    message: str
    dataset_loaded: bool