"""
Service layer for task operations.
Handles business logic for task management.
"""
from typing import List, Optional
from sqlmodel import Session, select
from ..models.task import Task, TaskCreate, TaskUpdate, TaskRead, TaskStatus


def create_task(session: Session, task_data: TaskCreate) -> TaskRead:
    """
    Create a new task in the database.

    Args:
        session: Database session
        task_data: Task creation data

    Returns:
        TaskRead: The created task
    """
    task = Task.model_validate(task_data)
    session.add(task)
    session.commit()
    session.refresh(task)
    return TaskRead.model_validate(task)


def get_task_by_id(session: Session, task_id: str) -> Optional[TaskRead]:
    """
    Retrieve a specific task by its ID.

    Args:
        session: Database session
        task_id: UUID of the task to retrieve

    Returns:
        TaskRead: The requested task or None if not found
    """
    statement = select(Task).where(Task.id == task_id)
    task = session.exec(statement).first()
    if task:
        return TaskRead.model_validate(task)
    return None


def get_all_tasks(
    session: Session,
    skip: int = 0,
    limit: int = 100,
    completed: Optional[bool] = None
) -> List[TaskRead]:
    """
    Retrieve all tasks with optional filtering and pagination.

    Args:
        session: Database session
        skip: Number of tasks to skip (for pagination)
        limit: Maximum number of tasks to return (for pagination)
        completed: Filter by completion status (optional)

    Returns:
        List[TaskRead]: List of tasks
    """
    statement = select(Task)

    # Apply filter if completed status is specified
    if completed is not None:
        if completed:
            statement = statement.where(Task.status == TaskStatus.completed)
        else:
            statement = statement.where(Task.status != TaskStatus.completed)

    # Apply pagination
    statement = statement.offset(skip).limit(limit)

    tasks = session.exec(statement).all()
    return [TaskRead.model_validate(task) for task in tasks]


def update_task(
    session: Session,
    task_id: str,
    task_data: TaskUpdate
) -> Optional[TaskRead]:
    """
    Update an existing task.

    Args:
        session: Database session
        task_id: UUID of the task to update
        task_data: Task update data

    Returns:
        TaskRead: The updated task or None if not found
    """
    task = session.get(Task, task_id)
    if not task:
        return None

    # Update only the fields that were provided in task_data
    update_data = task_data.model_dump(exclude_unset=True)

    # Update the updated_at timestamp when the task is modified
    if 'updated_at' not in update_data:
        from datetime import datetime
        update_data['updated_at'] = datetime.now()

    for field, value in update_data.items():
        setattr(task, field, value)

    session.add(task)
    session.commit()
    session.refresh(task)
    return TaskRead.model_validate(task)


def delete_task(session: Session, task_id: str) -> bool:
    """
    Delete a task by its ID.

    Args:
        session: Database session
        task_id: UUID of the task to delete

    Returns:
        bool: True if the task was deleted, False if not found
    """
    task = session.get(Task, task_id)
    if not task:
        return False

    session.delete(task)
    session.commit()
    return True