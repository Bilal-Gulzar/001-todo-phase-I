import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.models.task import Task


class TestTask:
    """Unit tests for the Task class."""

    def test_create_task_with_valid_data(self):
        """Test creating a task with valid data."""
        task = Task(id="123", title="Test task", status="pending")

        assert task.id == "123"
        assert task.title == "Test task"
        assert task.status == "pending"
        assert not task.is_completed

    def test_create_task_auto_generates_id_if_empty(self):
        """Test that ID is auto-generated when not provided."""
        task = Task(id="", title="Test task", status="pending")

        assert task.id != ""
        assert len(task.id) > 0

    def test_create_task_defaults_to_pending_status(self):
        """Test that status defaults to 'pending' when not specified."""
        task = Task(id="123", title="Test task")

        assert task.status == "pending"

    def test_create_task_fails_with_empty_title(self):
        """Test that creating a task with empty title raises ValueError."""
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            Task(id="123", title="", status="pending")

    def test_create_task_fails_with_invalid_status(self):
        """Test that creating a task with invalid status raises ValueError."""
        with pytest.raises(ValueError, match="Task status must be either 'pending' or 'completed'"):
            Task(id="123", title="Test task", status="invalid")

    def test_complete_task_changes_status(self):
        """Test that completing a task changes its status."""
        task = Task(id="123", title="Test task", status="pending")

        task.complete()

        assert task.status == "completed"
        assert task.is_completed

    def test_is_completed_property(self):
        """Test the is_completed property."""
        pending_task = Task(id="123", title="Pending task", status="pending")
        completed_task = Task(id="456", title="Completed task", status="completed")

        assert not pending_task.is_completed
        assert completed_task.is_completed