"""
Data downloader utility for Titanic dataset
"""
import os
import requests
import pandas as pd
from pathlib import Path
from config import TITANIC_DATA_URL, TITANIC_DATA_PATH, DATA_DIR

def download_titanic_dataset():
    """Download Titanic dataset if not already present."""
    
    # Create data directory if it doesn't exist
    DATA_DIR.mkdir(exist_ok=True)
    
    # Check if dataset already exists
    if TITANIC_DATA_PATH.exists():
        print(f"Dataset already exists at {TITANIC_DATA_PATH}")
        return True
    
    try:
        print("Downloading Titanic dataset...")
        response = requests.get(TITANIC_DATA_URL)
        response.raise_for_status()
        
        # Save the dataset
        with open(TITANIC_DATA_PATH, 'w') as f:
            f.write(response.text)
        
        print(f"Dataset successfully downloaded to {TITANIC_DATA_PATH}")
        
        # Verify the download by loading with pandas
        df = pd.read_csv(TITANIC_DATA_PATH)
        print(f"Dataset shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        return True
        
    except Exception as e:
        print(f"Error downloading dataset: {str(e)}")
        return False

def load_titanic_data():
    """Load the Titanic dataset."""
    if not TITANIC_DATA_PATH.exists():
        if not download_titanic_dataset():
            raise FileNotFoundError("Could not download Titanic dataset")
    
    return pd.read_csv(TITANIC_DATA_PATH)

if __name__ == "__main__":
    download_titanic_dataset()