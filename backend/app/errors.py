"""
Custom error handling for the application.
"""
from fastapi import HTTPException, status
from typing import Optional


class TaskNotFoundError(HTTPException):
    """
    Exception raised when a task is not found.
    """
    def __init__(self, task_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )


class ValidationError(HTTPException):
    """
    Exception for validation errors.
    """
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class DatabaseError(HTTPException):
    """
    Exception for database-related errors.
    """
    def __init__(self, detail: str = "Database error occurred"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


def handle_error(error_msg: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
    """
    Generic error handler function.

    Args:
        error_msg: The error message to return
        status_code: The HTTP status code (default 500)

    Returns:
        HTTPException with the given status code and message
    """
    return HTTPException(
        status_code=status_code,
        detail=error_msg
    )