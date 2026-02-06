from typing import List, Optional
from ..models.task import Task


class TodoManager:
    """
    Manages the collection of tasks in the Todo application.

    This class handles all business logic related to task management,
    including adding, listing, retrieving, completing, and deleting tasks.
    All data is stored in-memory for this implementation.
    """

    def __init__(self) -> None:
        """Initialize the TodoManager with an empty task list."""
        self._tasks: List[Task] = []

    def add_task(self, title: str) -> Task:
        """
        Add a new task to the manager.

        Args:
            title: The title/description of the task

        Returns:
            The newly created Task object

        Raises:
            ValueError: If the title is empty or invalid
        """
        task = Task(id="", title=title)  # ID will be auto-generated
        self._tasks.append(task)
        return task

    def list_tasks(self) -> List[Task]:
        """
        Get all tasks in the manager.

        Returns:
            A list of all Task objects
        """
        return self._tasks.copy()

    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Retrieve a specific task by its ID.

        Args:
            task_id: The ID of the task to retrieve

        Returns:
            The Task object if found, None otherwise
        """
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    def complete_task(self, task_id: str) -> bool:
        """
        Mark a task as completed.

        Args:
            task_id: The ID of the task to complete

        Returns:
            True if the task was found and updated, False otherwise
        """
        task = self.get_task(task_id)
        if task:
            task.complete()
            return True
        return False

    def delete_task(self, task_id: str) -> bool:
        """
        Remove a task from the manager.

        Args:
            task_id: The ID of the task to delete

        Returns:
            True if the task was found and deleted, False otherwise
        """
        for i, task in enumerate(self._tasks):
            if task.id == task_id:
                del self._tasks[i]
                return True
        return False

    @property
    def task_count(self) -> int:
        """
        Get the total number of tasks.

        Returns:
            The count of tasks in the manager
        """
        return len(self._tasks)

    def get_pending_tasks(self) -> List[Task]:
        """
        Get all pending tasks.

        Returns:
            A list of tasks with 'pending' status
        """
        return [task for task in self._tasks if not task.is_completed]

    def get_completed_tasks(self) -> List[Task]:
        """
        Get all completed tasks.

        Returns:
            A list of tasks with 'completed' status
        """
        return [task for task in self._tasks if task.is_completed]