"""
Database reset script - drops all tables and recreates them.
Use this when you need to reset the database schema.

WARNING: This will delete all data in the database!
"""
from app.database import engine
from app.models.user import User
from app.models.task import Task
from sqlmodel import SQLModel

def reset_database():
    """
    Drop all tables and recreate them with the current schema.
    """
    print("WARNING: This will delete all data in the database!")
    print("Dropping all tables...")

    # Drop all tables
    SQLModel.metadata.drop_all(engine)
    print("All tables dropped")

    # Create all tables with new schema
    print("Creating tables with new schema...")
    SQLModel.metadata.create_all(engine)
    print("Tables created successfully")
    print("\nDatabase reset complete!")
    print("New schema includes:")
    print("  - User table (id, email, password_hash, full_name, created_at)")
    print("  - Task table (id, user_id, title, description, status, priority, created_at, updated_at)")

if __name__ == "__main__":
    reset_database()
