"""
Data analysis functions for Titanic dataset
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, Optional, List
import base64
import io
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from download_data import load_titanic_data

# Load dataset globally
try:
    df = load_titanic_data()
    print(f"Loaded Titanic dataset with {len(df)} rows")
except Exception as e:
    print(f"Error loading dataset: {e}")
    df = pd.DataFrame()

class TitanicAnalyzer:
    def __init__(self):
        self.df = df.copy() if not df.empty else pd.DataFrame()
        
    def get_basic_stats(self) -> Dict[str, Any]:
        """Get basic statistics about the dataset."""
        if self.df.empty:
            return {"error": "Dataset not loaded"}
        
        return {
            "total_passengers": int(len(self.df)),
            "survivors": int(self.df['Survived'].sum()),
            "survival_rate": float(self.df['Survived'].mean() * 100),
            "male_passengers": int((self.df['Sex'] == 'male').sum()),
            "female_passengers": int((self.df['Sex'] == 'female').sum()),
            "male_percentage": float((self.df['Sex'] == 'male').mean() * 100),
            "average_age": float(self.df['Age'].mean()),
            "average_fare": float(self.df['Fare'].mean()),
            "classes": [int(x) for x in sorted(self.df['Pclass'].unique().tolist())],
        }
    
    def get_survival_by_gender(self) -> Dict[str, Any]:
        """Analyze survival rates by gender."""
        survival_by_gender = self.df.groupby('Sex')['Survived'].agg(['count', 'sum', 'mean']).round(3)
        return {
            "male_survival_rate": float(survival_by_gender.loc['male', 'mean'] * 100),
            "female_survival_rate": float(survival_by_gender.loc['female', 'mean'] * 100),
            "male_survivors": int(survival_by_gender.loc['male', 'sum']),
            "female_survivors": int(survival_by_gender.loc['female', 'sum']),
            "total_male": int(survival_by_gender.loc['male', 'count']),
            "total_female": int(survival_by_gender.loc['female', 'count'])
        }
    
    def get_survival_by_class(self) -> Dict[str, Any]:
        """Analyze survival rates by passenger class."""
        survival_by_class = self.df.groupby('Pclass')['Survived'].agg(['count', 'sum', 'mean']).round(3)
        result = {}
        for pclass in sorted(self.df['Pclass'].unique()):
            result[f"class_{pclass}"] = {
                "survival_rate": float(survival_by_class.loc[pclass, 'mean'] * 100),
                "survivors": int(survival_by_class.loc[pclass, 'sum']),
                "total": int(survival_by_class.loc[pclass, 'count'])
            }
        return result
    
    def get_age_statistics(self) -> Dict[str, Any]:
        """Get age-related statistics."""
        age_data = self.df['Age'].dropna()
        return {
            "average_age": float(age_data.mean()),
            "median_age": float(age_data.median()),
            "min_age": float(age_data.min()),
            "max_age": float(age_data.max()),
            "age_std": float(age_data.std()),
            "age_ranges": {
                "children_0_12": int(len(age_data[age_data <= 12])),
                "teens_13_19": int(len(age_data[(age_data > 12) & (age_data <= 19)])),
                "adults_20_59": int(len(age_data[(age_data > 19) & (age_data <= 59)])),
                "seniors_60_plus": int(len(age_data[age_data > 59]))
            }
        }
    
    def get_embarkation_stats(self) -> Dict[str, Any]:
        """Get embarkation port statistics."""
        embark_counts = self.df['Embarked'].value_counts()
        embark_mapping = {'C': 'Cherbourg', 'Q': 'Queenstown', 'S': 'Southampton'}
        
        result = {}
        for port_code, count in embark_counts.items():
            port_name = embark_mapping.get(port_code, str(port_code))
            result[port_name] = {
                "count": int(count),
                "percentage": float(count / len(self.df) * 100)
            }
        return result
    
    def create_age_histogram_plotly(self) -> str:
        """Create age histogram using Plotly."""
        age_data = self.df['Age'].dropna()
        
        fig = px.histogram(
            x=age_data, 
            nbins=20,
            title="Age Distribution of Titanic Passengers",
            labels={'x': 'Age', 'y': 'Count'},
            color_discrete_sequence=['#1f77b4']
        )
        fig.update_layout(height=400, width=600)
        
        return fig.to_html(include_plotlyjs='cdn')
    
    def create_survival_by_class_chart(self) -> str:
        """Create survival by class chart."""
        survival_data = self.df.groupby(['Pclass', 'Survived']).size().unstack(fill_value=0)
        survival_rate = self.df.groupby('Pclass')['Survived'].mean() * 100
        
        fig = go.Figure()
        fig.add_bar(x=['1st Class', '2nd Class', '3rd Class'], 
                   y=survival_rate.values,
                   name='Survival Rate (%)',
                   marker_color=['#2E86AB', '#A23B72', '#F18F01'])
        
        fig.update_layout(
            title="Survival Rate by Passenger Class",
            xaxis_title="Passenger Class",
            yaxis_title="Survival Rate (%)",
            height=400,
            width=600
        )
        
        return fig.to_html(include_plotlyjs='cdn')
    
    def create_gender_survival_chart(self) -> str:
        """Create gender survival chart."""
        survival_data = self.df.groupby('Sex')['Survived'].mean() * 100
        
        fig = px.bar(
            x=['Female', 'Male'], 
            y=[survival_data['female'], survival_data['male']],
            title="Survival Rate by Gender",
            labels={'x': 'Gender', 'y': 'Survival Rate (%)'},
            color=['Female', 'Male'],
            color_discrete_map={'Female': '#E91E63', 'Male': '#2196F3'}
        )
        fig.update_layout(height=400, width=600)
        
        return fig.to_html(include_plotlyjs='cdn')
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """Answer specific questions about the dataset."""
        question_lower = question.lower()
        
        # Basic statistics
        if any(word in question_lower for word in ['total', 'how many', 'count']):
            if 'passenger' in question_lower:
                return {"answer": f"There were {len(self.df)} passengers on the Titanic.", "data": self.get_basic_stats()}
        
        # Gender questions
        if any(word in question_lower for word in ['male', 'female', 'gender']):
            gender_stats = self.get_survival_by_gender()
            if 'percentage' in question_lower and 'male' in question_lower:
                return {
                    "answer": f"{gender_stats['total_male']} passengers were male, which is {(gender_stats['total_male']/len(self.df)*100):.1f}% of all passengers.",
                    "data": gender_stats
                }
            elif 'survival' in question_lower:
                return {
                    "answer": f"Female survival rate: {gender_stats['female_survival_rate']:.1f}%, Male survival rate: {gender_stats['male_survival_rate']:.1f}%",
                    "data": gender_stats
                }
        
        # Age questions
        if any(word in question_lower for word in ['age', 'old', 'young']):
            age_stats = self.get_age_statistics()
            if 'average' in question_lower:
                return {
                    "answer": f"The average age of passengers was {age_stats['average_age']:.1f} years.",
                    "data": age_stats
                }
        
        # Fare questions
        if any(word in question_lower for word in ['fare', 'ticket', 'price', 'cost']):
            basic_stats = self.get_basic_stats()
            return {
                "answer": f"The average ticket fare was £{basic_stats['average_fare']:.2f}.",
                "data": basic_stats
            }
        
        # Embarkation questions
        if any(word in question_lower for word in ['embark', 'port', 'board']):
            embark_stats = self.get_embarkation_stats()
            return {
                "answer": "Passengers embarked from: " + ", ".join([f"{port}: {data['count']}" for port, data in embark_stats.items()]),
                "data": embark_stats
            }
        
        # Class questions
        if any(word in question_lower for word in ['class', 'first', 'second', 'third']):
            class_stats = self.get_survival_by_class()
            return {
                "answer": f"Class survival rates: 1st: {class_stats['class_1']['survival_rate']:.1f}%, 2nd: {class_stats['class_2']['survival_rate']:.1f}%, 3rd: {class_stats['class_3']['survival_rate']:.1f}%",
                "data": class_stats
            }
        
        # Default response
        return {
            "answer": "I can help you analyze the Titanic dataset. Try asking about passenger demographics, survival rates, ages, fares, or embarkation ports.",
            "data": self.get_basic_stats()
        }