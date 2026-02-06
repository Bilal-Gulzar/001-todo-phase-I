"""
Database module for handling database connections and initialization.
"""
from sqlmodel import SQLModel, create_engine
from sqlalchemy import event
from sqlalchemy.pool import Pool
import os
from typing import Optional
from contextlib import contextmanager
from .config import settings


# Create engine with Neon-compatible settings
connection_string = settings.database_url
engine = create_engine(connection_string, echo=settings.db_echo)


def create_db_and_tables():
    """
    Creates all database tables if they don't exist.
    This should be called on application startup.
    """
    print("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    print("Database tables created successfully.")


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite-specific pragmas if using SQLite (for local dev)."""
    if dbapi_connection is not None:
        cursor = dbapi_connection.cursor()
        # Set any SQLite-specific settings if needed
        cursor.close()


def get_session():
    """
    Get a database session.
    This function is typically used with FastAPI's dependency injection.
    """
    from sqlmodel import Session
    with Session(engine) as session:
        yield session


# Context manager for database sessions
@contextmanager
def get_db_session():
    """
    Context manager to get a database session.
    Ensures proper cleanup of resources.
    """
    from sqlmodel import Session
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()