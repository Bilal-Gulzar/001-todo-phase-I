"""
Authentication API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from ..database import get_db_session
from ..models.user import User, UserCreate, UserRead
from ..core.security import hash_password, verify_password, create_access_token

router = APIRouter()


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, session: Session = Depends(get_db_session)):
    """
    Create a new user account.

    Args:
        user_data: User registration data (email, password, full_name)
        session: Database session

    Returns:
        Created user data (without password)

    Raises:
        HTTPException: 400 if email already exists
    """
    # Check if user with this email already exists
    statement = select(User).where(User.email == user_data.email)
    existing_user = session.exec(statement).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash the password
    password_hash = hash_password(user_data.password)

    # Create new user
    new_user = User(
        email=user_data.email,
        password_hash=password_hash,
        full_name=user_data.full_name
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_db_session)
):
    """
    Login with email and password to get access token.

    Args:
        form_data: OAuth2 form with username (email) and password
        session: Database session

    Returns:
        Access token and token type

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Find user by email (username field in OAuth2 form)
    statement = select(User).where(User.email == form_data.username)
    user = session.exec(statement).first()

    # Verify user exists and password is correct
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(data={"sub": user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name
        }
    }
