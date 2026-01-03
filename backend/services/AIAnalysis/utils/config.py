from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    MISTRAL_API_KEY: str
    MONGO_URI: str
    DATABASE_NAME: str = "ai_analysis_db"
    NOTIFICATION_SERVICE_URL: str 
    USER_SERVICE_URL: str 
    SIMILARITY_THRESHOLD: float = 0.85
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
