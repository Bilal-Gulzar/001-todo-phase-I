"""
API endpoints for task management.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlmodel import Session
from ..database import get_db_session
from ..models.task import Task, TaskCreate, TaskUpdate, TaskRead
from ..services.task_service import (
    create_task,
    get_task_by_id,
    get_all_tasks,
    update_task,
    delete_task
)

router = APIRouter()


@router.post("/tasks", response_model=TaskRead, status_code=201)
def create_new_task(task_data: TaskCreate, session: Session = Depends(get_db_session)):
    """
    Create a new task.

    Args:
        task_data: Task creation data
        session: Database session

    Returns:
        TaskRead: The created task
    """
    try:
        return create_task(session, task_data)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/tasks", response_model=List[TaskRead])
def list_all_tasks(
    skip: int = 0,
    limit: int = 100,
    completed: bool = None,
    session: Session = Depends(get_db_session)
):
    """
    List all tasks with optional filtering and pagination.

    Args:
        skip: Number of tasks to skip (for pagination)
        limit: Maximum number of tasks to return (for pagination)
        completed: Filter by completion status (optional)
        session: Database session

    Returns:
        List[TaskRead]: List of tasks
    """
    try:
        return get_all_tasks(session, skip=skip, limit=limit, completed=completed)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}", response_model=TaskRead)
def get_single_task(task_id: str, session: Session = Depends(get_db_session)):
    """
    Get a specific task by ID.

    Args:
        task_id: UUID of the task to retrieve
        session: Database session

    Returns:
        TaskRead: The requested task
    """
    try:
        task = get_task_by_id(session, task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/tasks/{task_id}", response_model=TaskRead)
def update_existing_task(
    task_id: str,
    task_data: TaskUpdate,
    session: Session = Depends(get_db_session)
):
    """
    Update a specific task by ID.

    Args:
        task_id: UUID of the task to update
        task_data: Task update data
        session: Database session

    Returns:
        TaskRead: The updated task
    """
    try:
        task = update_task(session, task_id, task_data)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/tasks/{task_id}", status_code=204)
def remove_task(task_id: str, session: Session = Depends(get_db_session)):
    """
    Delete a specific task by ID.

    Args:
        task_id: UUID of the task to delete
        session: Database session

    Returns:
        None: 204 No Content on successful deletion
    """
    try:
        success = delete_task(session, task_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
        return None  # 204 No Content
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))