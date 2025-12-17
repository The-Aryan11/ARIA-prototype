"""
ARIA Configuration - Environment Settings
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment"""
    
    # Application
    APP_NAME: str = "ARIA"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Security
    SECRET_KEY: str = "change-me-in-production"
    
    # Groq AI (FREE)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    # PostgreSQL (Neon FREE)
    POSTGRES_URL: str = ""
    
    # MongoDB Atlas (FREE)
    MONGODB_URL: str = ""
    MONGODB_DB_NAME: str = "aria"
    
    # Redis (Upstash FREE)
    REDIS_URL: str = ""
    
    # Twilio WhatsApp
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_WHATSAPP_NUMBER: str = "whatsapp:+14155238886"
    
    # Sentry
    SENTRY_DSN: Optional[str] = None
    
    # Features
    ENABLE_COLOR_ANALYSIS: bool = True
    ENABLE_SOCIAL_PROOF: bool = True
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()


settings = get_settings()