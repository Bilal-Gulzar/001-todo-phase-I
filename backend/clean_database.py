"""
Database Cleaning Script - Wipes Chat History for Fresh Start
Run this to delete all chat history and give the AI a blank slate.
"""
import os
from sqlmodel import Session, select, delete
from app.database import engine
from app.models.task import Task

def clean_database():
    """Delete all tasks and chat history from the database."""
    print("🧹 Starting database cleanup...")

    try:
        with Session(engine) as session:
            # Delete all tasks
            statement = delete(Task)
            result = session.exec(statement)
            session.commit()

            print(f"✅ Deleted {result.rowcount} tasks from database")
            print("✅ Database is now clean - AI has a blank slate!")

    except Exception as e:
        print(f"❌ Error cleaning database: {e}")
        return False

    return True

if __name__ == "__main__":
    print("=" * 50)
    print("DATABASE CLEANUP SCRIPT")
    print("=" * 50)
    clean_database()
    print("=" * 50)
