"""
Task model definition using SQLModel.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid
from typing import Optional


class TaskBase(SQLModel):
    """
    Base model for Task containing common fields.
    """
    title: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    is_completed: bool = Field(default=False)


class Task(TaskBase, table=True):
    """
    Task model representing a task in the system.

    Attributes:
        id: Unique identifier for the task (UUID)
        title: Title of the task (required, 1-100 characters)
        description: Optional description of the task (max 500 characters)
        is_completed: Status indicating if the task is completed (default: false)
        created_at: Timestamp when the task was created (auto-populated)
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)


class TaskCreate(TaskBase):
    """
    Model for creating a new task.
    Contains the fields required when creating a new task.
    """
    pass  # Inherit all fields from TaskBase


class TaskUpdate(SQLModel):
    """
    Model for updating an existing task.
    Contains optional fields that can be updated.
    """
    title: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    is_completed: Optional[bool] = None


class TaskRead(TaskBase):
    """
    Model for reading a task with its ID and creation timestamp.
    """
    id: str
    created_at: datetime