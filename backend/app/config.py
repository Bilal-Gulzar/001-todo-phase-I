"""
Configuration module for the application settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    app_name: str = "Todo Backend API"
    database_url: str = "sqlite:///./todo_local.db"  # Default for local development
    db_echo: bool = False  # Set to False for production
    debug: bool = False
    gemini_api_key: Optional[str] = None  # Gemini API key for AI agent
    groq_api_key: Optional[str] = None  # Groq API key for AI agent

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False  # Allow DATABASE_URL to map to database_url


# Initialize settings and override with environment variables explicitly
settings = Settings()

# Explicitly check for DATABASE_URL environment variable (for Kubernetes)
if os.getenv("DATABASE_URL"):
    settings.database_url = os.getenv("DATABASE_URL")
    print(f"✅ Using DATABASE_URL from environment: {settings.database_url[:30]}...")

if os.getenv("GROQ_API_KEY"):
    settings.groq_api_key = os.getenv("GROQ_API_KEY")
    print("✅ GROQ_API_KEY loaded from environment")

if os.getenv("DB_ECHO"):
    settings.db_echo = os.getenv("DB_ECHO").lower() == "true"

if os.getenv("DEBUG"):
    settings.debug = os.getenv("DEBUG").lower() == "true"