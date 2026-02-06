from dataclasses import dataclass
from typing import Optional
from uuid import uuid4


@dataclass
class Task:
    """
    Represents a task in the Todo application.

    Attributes:
        id (str): Unique identifier for the task
        title (str): Description of the task
        status (str): Current status of the task ('pending' or 'completed')
    """
    id: str
    title: str
    status: str = "pending"

    def __post_init__(self):
        """Validate the task after initialization."""
        if not self.id:
            self.id = str(uuid4())

        if not self.title.strip():
            raise ValueError("Task title cannot be empty")

        if self.status not in ["pending", "completed"]:
            raise ValueError("Task status must be either 'pending' or 'completed'")

    @property
    def is_completed(self) -> bool:
        """Check if the task is completed."""
        return self.status == "completed"

    def complete(self) -> None:
        """Mark the task as completed."""
        self.status = "completed"