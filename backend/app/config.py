"""
Configuration module for the application settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    app_name: str = "Todo Backend API"
    database_url: str = "sqlite:///./todo_local.db"  # Default for local development
    db_echo: bool = True  # Set to True for SQL query logging during debugging
    debug: bool = True

    class Config:
        env_file = ".env"


settings = Settings()