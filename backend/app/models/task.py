"""
Task model definition using SQLModel.
"""
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
import uuid
from typing import Optional
from enum import Enum


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in-progress"
    completed = "completed"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskBase(SQLModel):
    """
    Base model for Task containing common fields.
    """
    title: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    status: TaskStatus = Field(default=TaskStatus.pending)
    priority: TaskPriority = Field(default=TaskPriority.medium)


class Task(TaskBase, table=True):
    """
    Task model representing a task in the system.

    Attributes:
        id: Unique identifier for the task (UUID)
        user_id: Foreign key to the user who owns this task
        title: Title of the task (required, 1-100 characters)
        description: Optional description of the task (max 500 characters)
        status: Status of the task (pending, in-progress, completed)
        priority: Priority of the task (low, medium, high)
        created_at: Timestamp when the task was created (auto-populated)
        updated_at: Timestamp when the task was last updated (auto-populated)
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


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
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None


class TaskRead(TaskBase):
    """
    Model for reading a task with its ID and timestamps.
    """
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime