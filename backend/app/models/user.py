"""
User model definition using SQLModel.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid
from typing import Optional


class UserBase(SQLModel):
    """
    Base model for User containing common fields.
    """
    email: str = Field(unique=True, index=True, max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=100)


class User(UserBase, table=True):
    """
    User model representing a user in the system.

    Attributes:
        id: Unique identifier for the user (UUID)
        email: User's email address (unique, indexed)
        password_hash: Hashed password
        full_name: User's full name (optional)
        created_at: Timestamp when the user was created
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.now)


class UserCreate(SQLModel):
    """
    Model for creating a new user (signup).
    """
    email: str = Field(max_length=255)
    password: str = Field(min_length=6, max_length=100)
    full_name: Optional[str] = Field(default=None, max_length=100)


class UserRead(UserBase):
    """
    Model for reading user data (without password).
    """
    id: str
    created_at: datetime


class UserLogin(SQLModel):
    """
    Model for user login.
    """
    email: str
    password: str
