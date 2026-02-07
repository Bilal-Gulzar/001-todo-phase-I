"""
Database module for handling database connections and initialization.
"""
from sqlmodel import SQLModel, create_engine
from sqlalchemy import event
from sqlalchemy.pool import Pool
import os
from typing import Optional, Generator
from .config import settings
import urllib.parse


# Parse and properly encode the connection string to handle special characters in password
def create_database_engine():
    """
    Creates a database engine with proper URL encoding for special characters in credentials.
    """
    connection_string = settings.database_url

    # Parse the connection string to extract components
    parsed = urllib.parse.urlparse(connection_string)

    # If this is a PostgreSQL URL, we need to handle special characters in the password
    if parsed.scheme.startswith('postgres'):
        # Extract username and password from netloc
        if '@' in parsed.netloc:
            credentials, host_part = parsed.netloc.split('@', 1)
            if ':' in credentials:
                username, password = credentials.split(':', 1)
                # URL encode the password to handle special characters
                encoded_password = urllib.parse.quote_plus(password)
                # Reconstruct the netloc with encoded password
                new_netloc = f"{username}:{encoded_password}@{host_part}"
            else:
                new_netloc = parsed.netloc

            # Reconstruct the URL with the properly encoded password
            connection_string = urllib.parse.urlunparse((
                parsed.scheme,
                new_netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment
            ))

    return create_engine(connection_string, echo=settings.db_echo)


# Create engine with Neon-compatible settings, handling URL encoding
engine = create_database_engine()


def create_db_and_tables():
    """
    Creates all database tables if they don't exist.
    This should be called on application startup.
    """
    print("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    print("Database tables created successfully.")


def get_session() -> Generator:
    """
    Get a database session.
    This function is typically used with FastAPI's dependency injection.
    """
    from sqlmodel import Session
    with Session(engine) as session:
        yield session


def get_db_session() -> Generator:
    """
    Get a database session for FastAPI dependency injection.
    This function is used with FastAPI's Depends().
    """
    from sqlmodel import Session
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()