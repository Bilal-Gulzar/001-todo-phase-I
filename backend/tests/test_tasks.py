"""
Tests for the task API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from app.main import app
from app.models.task import Task
from app.database import get_db_session
from uuid import uuid4


# Create an in-memory SQLite database for testing
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(bind=engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_db_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_create_task(client: TestClient):
    """Test creating a new task."""
    task_data = {
        "title": "Test Task",
        "description": "This is a test task"
    }

    response = client.post("/api/v1/tasks", json=task_data)
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "This is a test task"
    assert data["is_completed"] is False
    assert "id" in data
    assert "created_at" in data


def test_get_task(client: TestClient, session: Session):
    """Test retrieving a single task."""
    # Create a task first
    task = Task(
        title="Get Test Task",
        description="This is a get test task",
        is_completed=False
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    response = client.get(f"/api/v1/tasks/{task.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == task.id
    assert data["title"] == "Get Test Task"
    assert data["description"] == "This is a get test task"


def test_get_nonexistent_task(client: TestClient):
    """Test retrieving a task that doesn't exist."""
    fake_id = str(uuid4())
    response = client.get(f"/api/v1/tasks/{fake_id}")
    assert response.status_code == 404


def test_list_tasks(client: TestClient, session: Session):
    """Test listing all tasks."""
    # Create multiple tasks
    task1 = Task(title="Task 1", description="First task", is_completed=False)
    task2 = Task(title="Task 2", description="Second task", is_completed=True)
    session.add(task1)
    session.add(task2)
    session.commit()

    response = client.get("/api/v1/tasks")
    assert response.status_code == 200

    data = response.json()
    assert len(data) >= 2  # At least the 2 tasks we created plus any from other tests


def test_update_task(client: TestClient, session: Session):
    """Test updating a task."""
    # Create a task first
    task = Task(
        title="Original Task",
        description="Original description",
        is_completed=False
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    update_data = {
        "title": "Updated Task",
        "is_completed": True
    }

    response = client.patch(f"/api/v1/tasks/{task.id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Updated Task"
    assert data["is_completed"] is True


def test_delete_task(client: TestClient, session: Session):
    """Test deleting a task."""
    # Create a task first
    task = Task(
        title="Delete Test Task",
        description="This task will be deleted",
        is_completed=False
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    response = client.delete(f"/api/v1/tasks/{task.id}")
    assert response.status_code == 204

    # Verify the task was deleted
    response = client.get(f"/api/v1/tasks/{task.id}")
    assert response.status_code == 404


def test_validation_errors(client: TestClient):
    """Test validation for task creation."""
    # Empty title should fail validation
    invalid_task_data = {
        "title": "",  # Empty title not allowed
        "description": "Invalid task"
    }

    response = client.post("/api/v1/tasks", json=invalid_task_data)
    assert response.status_code == 422