"""
API endpoints for task management.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlmodel import Session
from ..database import get_db_session
from ..models.task import Task, TaskCreate, TaskUpdate, TaskRead
from ..models.user import User
from ..api.deps import get_current_user
from ..services.task_service import (
    create_task,
    get_task_by_id,
    get_all_tasks,
    update_task,
    delete_task
)

router = APIRouter()


@router.post("/tasks", response_model=TaskRead, status_code=201)
def create_new_task(
    task_data: TaskCreate,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new task for the current user.

    Args:
        task_data: Task creation data
        session: Database session
        current_user: Current authenticated user

    Returns:
        TaskRead: The created task
    """
    try:
        print(f"Creating new task for user {current_user.id} with data: {task_data}")
        result = create_task(session, task_data, current_user.id)
        print(f"Successfully created task with ID: {result.id}")
        return result
    except Exception as e:
        print(f'DB Error in create_new_task: {e}')
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=422, detail=f"Database error: {str(e)}")


@router.get("/tasks", response_model=List[TaskRead])
def list_all_tasks(
    skip: int = 0,
    limit: int = 100,
    completed: bool = None,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    List all tasks for the current user with optional filtering and pagination.

    Args:
        skip: Number of tasks to skip (for pagination)
        limit: Maximum number of tasks to return (for pagination)
        completed: Filter by completion status (optional)
        session: Database session
        current_user: Current authenticated user

    Returns:
        List[TaskRead]: List of tasks belonging to current user
    """
    try:
        print(f"Fetching tasks for user {current_user.id} with skip={skip}, limit={limit}, completed={completed}")
        result = get_all_tasks(session, current_user.id, skip=skip, limit=limit, completed=completed)
        print(f"Successfully fetched {len(result)} tasks")
        return result
    except Exception as e:
        print(f'DB Error in list_all_tasks: {e}')
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/tasks/{task_id}", response_model=TaskRead)
def get_single_task(
    task_id: str,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific task by ID (must belong to current user).

    Args:
        task_id: UUID of the task to retrieve
        session: Database session
        current_user: Current authenticated user

    Returns:
        TaskRead: The requested task
    """
    try:
        print(f"Fetching task with ID: {task_id} for user {current_user.id}")
        task = get_task_by_id(session, task_id, current_user.id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
        print(f"Successfully fetched task with ID: {task.id}")
        return task
    except HTTPException:
        raise
    except Exception as e:
        print(f'DB Error in get_single_task: {e}')
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.patch("/tasks/{task_id}", response_model=TaskRead)
def update_existing_task(
    task_id: str,
    task_data: TaskUpdate,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Update a specific task by ID (must belong to current user).

    Args:
        task_id: UUID of the task to update
        task_data: Task update data
        session: Database session
        current_user: Current authenticated user

    Returns:
        TaskRead: The updated task
    """
    try:
        print(f"Updating task with ID: {task_id} for user {current_user.id}, data: {task_data}")
        task = update_task(session, task_id, task_data, current_user.id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
        print(f"Successfully updated task with ID: {task.id}")
        return task
    except HTTPException:
        raise
    except Exception as e:
        print(f'DB Error in update_existing_task: {e}')
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.delete("/tasks/{task_id}", status_code=204)
def remove_task(
    task_id: str,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific task by ID (must belong to current user).

    Args:
        task_id: UUID of the task to delete
        session: Database session
        current_user: Current authenticated user

    Returns:
        None: 204 No Content on successful deletion
    """
    try:
        print(f"Deleting task with ID: {task_id} for user {current_user.id}")
        success = delete_task(session, task_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
        print(f"Successfully deleted task with ID: {task_id}")
        return None  # 204 No Content
    except HTTPException:
        raise
    except Exception as e:
        print(f'DB Error in remove_task: {e}')
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")