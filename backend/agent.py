"""
LangChain agent for Titanic dataset analysis with Gemini AI
"""
import os
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from typing import Dict, Any, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.data_analyzer import TitanicAnalyzer
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_TEMPERATURE, GEMINI_MAX_TOKENS

class TitanicAgent:
    def __init__(self):
        self.analyzer = TitanicAnalyzer()
        
        # Initialize Gemini
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.llm = ChatGoogleGenerativeAI(
                model=GEMINI_MODEL,
                temperature=GEMINI_TEMPERATURE,
                max_tokens=GEMINI_MAX_TOKENS,
                google_api_key=GEMINI_API_KEY
            )
            self.use_ai = True
            print("✅ Gemini AI initialized successfully")
        else:
            self.llm = None
            self.use_ai = False
            print("⚠️ No Gemini API key found. Using basic analyzer only.")
    
    def _get_dataset_context(self) -> str:    
        """Get dataset context for AI."""
        stats = self.analyzer.get_basic_stats()
        if 'error' in stats:
            return "Dataset not available."
        
        context = f"""
        Titanic Dataset Context:
        - Total passengers: {stats['total_passengers']}
        - Survivors: {stats['survivors']} (Survival rate: {stats['survival_rate']:.1f}%)
        - Male passengers: {stats['male_passengers']} ({stats['male_percentage']:.1f}%)
        - Female passengers: {stats['female_passengers']} ({100-stats['male_percentage']:.1f}%)
        - Average age: {stats['average_age']:.1f} years
        - Average fare: £{stats['average_fare']:.2f}
        - Passenger classes: {stats['classes']}
        
        Available analysis functions:
        - Basic statistics and demographics
        - Survival analysis by gender, class, age
        - Age distribution and fare analysis
        - Embarkation port statistics
        - Interactive visualizations (histograms, bar charts, survival analysis)
        """
        return context
        
    def _determine_chart_type(self, question: str, ai_response: str = "") -> tuple[Optional[str], Optional[str]]:
        """Determine if a chart should be shown and what type."""
        question_lower = question.lower()
        response_lower = ai_response.lower()
        
        # Check for explicit visualization requests
        viz_keywords = ['chart', 'graph', 'plot', 'histogram', 'show', 'visualize', 'display']
        if any(word in question_lower for word in viz_keywords):
            if any(word in question_lower for word in ['age']):
                return self.analyzer.create_age_histogram_plotly(), "age_histogram"
            elif any(word in question_lower for word in ['class', 'survival']):
                return self.analyzer.create_survival_by_class_chart(), "survival_by_class"
            elif any(word in question_lower for word in ['gender', 'male', 'female']):
                return self.analyzer.create_gender_survival_chart(), "gender_survival"
        
        # Auto-generate charts based on question content
        if any(word in question_lower for word in ['age']) and 'distribution' in question_lower:
            return self.analyzer.create_age_histogram_plotly(), "age_histogram"
        elif 'class' in question_lower and any(word in question_lower for word in ['survival', 'survive']):
            return self.analyzer.create_survival_by_class_chart(), "survival_by_class"
        elif any(word in question_lower for word in ['gender', 'male', 'female']) and 'survival' in question_lower:
            return self.analyzer.create_gender_survival_chart(), "gender_survival"
        
        return None, None
        
    def process_query(self, question: str) -> Dict[str, Any]:
        """Process user query with AI enhancement."""
        
        if self.use_ai and self.llm:
            return self._process_with_ai(question)
        else:
            return self._process_without_ai(question)
    
    def _process_with_ai(self, question: str) -> Dict[str, Any]:
        """Process query using Gemini AI."""
        try:
            # Get relevant data for the question
            question_lower = question.lower()
            context_data = {}
            
            # Gather relevant data based on question type
            if any(word in question_lower for word in ['gender', 'male', 'female']):
                context_data.update(self.analyzer.get_survival_by_gender())
            if any(word in question_lower for word in ['class', 'first', 'second', 'third']):
                context_data.update(self.analyzer.get_survival_by_class())
            if any(word in question_lower for word in ['age', 'old', 'young']):
                context_data.update(self.analyzer.get_age_statistics())
            if any(word in question_lower for word in ['embark', 'port']):
                context_data.update(self.analyzer.get_embarkation_stats())
            
            # Always include basic stats
            basic_stats = self.analyzer.get_basic_stats()
            context_data.update(basic_stats)
            
            # Create system prompt
            system_prompt = f"""
            You are an expert data analyst specializing in the Titanic dataset. You provide clear, accurate, and insightful answers about the Titanic passengers based on the data.
            
            {self._get_dataset_context()}
            
            Current relevant data for this question:
            {context_data}
            
            Guidelines:
            - Provide specific numbers and percentages when available
            - Be conversational but accurate
            - If the user asks for visualization, mention that a chart will be shown
            - Keep responses concise but informative (2-4 sentences max)
            - Always base answers on the actual data provided
            """
            
            # Query the AI
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Question: {question}")
            ]
            
            ai_response = self.llm.invoke(messages)
            answer_text = ai_response.content
            
            # Determine if we need a chart
            chart_html, chart_type = self._determine_chart_type(question, answer_text)
            
            return {
                "answer": answer_text,
                "data": context_data,
                "chart_html": chart_html,
                "chart_type": chart_type
            }
            
        except Exception as e:
            print(f"AI processing error: {e}")
            # Fallback to basic analyzer
            return self._process_without_ai(question)
    
    def _process_without_ai(self, question: str) -> Dict[str, Any]:
        """Fallback processing without AI."""
        # Get basic answer from analyzer
        response = self.analyzer.answer_question(question)
        
        # Determine if we need a chart
        chart_html, chart_type = self._determine_chart_type(question)
        
        return {
            "answer": response["answer"],
            "data": response.get("data"),
            "chart_html": chart_html,
            "chart_type": chart_type
        }