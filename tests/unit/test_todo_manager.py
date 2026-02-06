import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.services.todo_manager import TodoManager
from src.models.task import Task


class TestTodoManager:
    """Unit tests for the TodoManager class."""

    def test_initialize_todo_manager(self):
        """Test initializing a TodoManager."""
        manager = TodoManager()

        assert manager.task_count == 0
        assert manager.list_tasks() == []
        assert manager.get_pending_tasks() == []
        assert manager.get_completed_tasks() == []

    def test_add_task(self):
        """Test adding a task to the manager."""
        manager = TodoManager()

        task = manager.add_task("Test task")

        assert manager.task_count == 1
        assert task in manager.list_tasks()
        assert task.title == "Test task"
        assert task.status == "pending"

    def test_add_task_fails_with_empty_title(self):
        """Test that adding a task with empty title raises ValueError."""
        manager = TodoManager()

        with pytest.raises(ValueError):
            manager.add_task("")

    def test_list_tasks_returns_copy_of_internal_list(self):
        """Test that list_tasks returns a copy of the internal list."""
        manager = TodoManager()
        manager.add_task("Test task")

        original_tasks = manager.list_tasks()
        manager.add_task("Another task")

        assert len(original_tasks) == 1  # Original list not affected by addition

    def test_get_task_by_id(self):
        """Test retrieving a task by its ID."""
        manager = TodoManager()
        task = manager.add_task("Test task")

        retrieved_task = manager.get_task(task.id)

        assert retrieved_task is not None
        assert retrieved_task.id == task.id
        assert retrieved_task.title == task.title

    def test_get_task_returns_none_for_nonexistent_id(self):
        """Test that get_task returns None for nonexistent IDs."""
        manager = TodoManager()

        task = manager.get_task("nonexistent")

        assert task is None

    def test_complete_task_updates_status(self):
        """Test that completing a task updates its status."""
        manager = TodoManager()
        task = manager.add_task("Test task")

        result = manager.complete_task(task.id)

        assert result is True
        assert task.status == "completed"
        assert task.is_completed

    def test_complete_task_returns_false_for_nonexistent_id(self):
        """Test that complete_task returns False for nonexistent IDs."""
        manager = TodoManager()

        result = manager.complete_task("nonexistent")

        assert result is False

    def test_delete_task_removes_task(self):
        """Test that deleting a task removes it from the manager."""
        manager = TodoManager()
        task = manager.add_task("Test task")

        result = manager.delete_task(task.id)

        assert result is True
        assert manager.task_count == 0
        assert manager.get_task(task.id) is None

    def test_delete_task_returns_false_for_nonexistent_id(self):
        """Test that delete_task returns False for nonexistent IDs."""
        manager = TodoManager()

        result = manager.delete_task("nonexistent")

        assert result is False

    def test_task_count_property(self):
        """Test the task_count property."""
        manager = TodoManager()

        assert manager.task_count == 0

        manager.add_task("Task 1")
        assert manager.task_count == 1

        manager.add_task("Task 2")
        assert manager.task_count == 2

    def test_get_pending_tasks(self):
        """Test retrieving pending tasks."""
        manager = TodoManager()
        pending_task = manager.add_task("Pending task")
        completed_task = manager.add_task("Completed task")
        manager.complete_task(completed_task.id)

        pending_tasks = manager.get_pending_tasks()

        assert len(pending_tasks) == 1
        assert pending_task in pending_tasks
        assert completed_task not in pending_tasks

    def test_get_completed_tasks(self):
        """Test retrieving completed tasks."""
        manager = TodoManager()
        pending_task = manager.add_task("Pending task")
        completed_task = manager.add_task("Completed task")
        manager.complete_task(completed_task.id)

        completed_tasks = manager.get_completed_tasks()

        assert len(completed_tasks) == 1
        assert completed_task in completed_tasks
        assert pending_task not in completed_tasks