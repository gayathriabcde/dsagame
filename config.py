"""Configuration module for loading environment variables."""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration from environment variables."""
    
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    DB_NAME = os.getenv('DB_NAME', 'adaptive_tutor')
    INITIAL_MASTERY = float(os.getenv('INITIAL_MASTERY', '0.25'))
    LEARN_GAIN = float(os.getenv('LEARN_GAIN', '0.08'))
    ERROR_PENALTY = float(os.getenv('ERROR_PENALTY', '0.12'))
    MIN_MASTERY = float(os.getenv('MIN_MASTERY', '0.05'))
    MAX_MASTERY = float(os.getenv('MAX_MASTERY', '0.95'))
