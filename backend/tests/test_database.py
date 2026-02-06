"""
Tests for database initialization and connectivity.
"""
import pytest
from sqlmodel import Session, SQLModel, create_engine
from app.database import create_db_and_tables
from app.models.task import Task


def test_database_initialization():
    """Test that database tables are created properly."""
    # Create an in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:")

    # Attempt to create tables
    try:
        create_db_and_tables()
        # If we get here without exception, initialization succeeded
        assert True
    except Exception as e:
        # If there's an exception, initialization failed
        assert False, f"Database initialization failed: {e}"


def test_table_creation():
    """Test that the Task table can be created and used."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(bind=engine)

    # Create a session and try to interact with the Task table
    with Session(engine) as session:
        # Create a sample task
        task = Task(
            title="Test Task",
            description="This is a test task for database validation"
        )

        session.add(task)
        session.commit()
        session.refresh(task)

        # Verify the task was saved
        assert task.id is not None
        assert task.title == "Test Task"
        assert task.description == "This is a test task for database validation"

        # Query the task back
        retrieved_task = session.get(Task, task.id)
        assert retrieved_task is not None
        assert retrieved_task.id == task.id
        assert retrieved_task.title == task.title