"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/forex_ai_signals"
    DATABASE_URL_ASYNC: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/forex_ai_signals"
    USE_SQLITE: bool = True
    SQLITE_URL: str = "sqlite:///./forex_ai_signals.db"
    
    # JWT Settings
    JWT_SECRET_KEY: str = "forex-ai-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Market Data API
    TWELVEDATA_API_KEY: Optional[str] = None
    TWELVEDATA_BASE_URL: str = "https://api.twelvedata.com"
    FINNHUB_API_KEY: Optional[str] = None
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Admin
    ADMIN_EMAIL: str = "admin@forexai.com"
    ADMIN_PASSWORD: str = "admin123"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
