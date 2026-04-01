"""
Configuration settings for the Language Detection API
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings"""
    
    # Model settings
    MODEL_PATH: str = os.getenv('MODEL_PATH', 'models/lid.176.bin')
    CONFIDENCE_THRESHOLD: float = float(os.getenv('CONFIDENCE_THRESHOLD', '0.6'))
    
    # API settings
    API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
    API_PORT: int = int(os.getenv('API_PORT', '8000'))
    API_RELOAD: bool = os.getenv('API_RELOAD', 'false').lower() == 'true'
    
    # CORS settings
    CORS_ORIGINS: List[str] = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')
    
    # Redis settings (optional)
    REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost:6379')
    REDIS_ENABLED: bool = os.getenv('REDIS_ENABLED', 'true').lower() == 'true'
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = int(os.getenv('RATE_LIMIT_REQUESTS_PER_MINUTE', '30'))
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', 'logs/language_detection.log')
    
    # Application info
    APP_NAME: str = "Language Detection API"
    APP_VERSION: str = "2.0.0"
    APP_DESCRIPTION: str = "Production-ready language detection using FastText with 150+ language support"
    
    @classmethod
    def get_model_path(cls) -> str:
        """Get full model path"""
        if not os.path.isabs(cls.MODEL_PATH):
            return os.path.join(os.path.dirname(os.path.dirname(__file__)), cls.MODEL_PATH)
        return cls.MODEL_PATH
    
    @classmethod
    def get_log_file_path(cls) -> str:
        """Get full log file path"""
        if not os.path.isabs(cls.LOG_FILE):
            return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), cls.LOG_FILE)
        return cls.LOG_FILE

# Global settings instance
settings = Settings()
