from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional

from ..database import get_db
from . import schemas, models, jwt as auth_jwt
from .jwt import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_active_user

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
    responses={401: {"description": "Unauthorized"}},
)

users_router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"],
)


def get_user_by_email(email: str, db: Session) -> Optional[models.User]:
    """Look up a user by email address."""
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(email: str, username: str, hashed_password: str, db: Session) -> models.User:
    """Create and persist a new user."""
    db_user = models.User(
        email=email,
        username=username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = get_user_by_email(user.email, db)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = models.User.get_password_hash(user.password)
    new_user = create_user(user.email, user.username, hashed_password, db)
    
    return {"id": new_user.id, "email": str(new_user.email)}

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Authenticate user
    user = auth_jwt.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    # Authenticate user
    user = auth_jwt.authenticate_user(user_credentials.email, user_credentials.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserResponse)
def get_current_user_info(current_user: models.User = Depends(get_current_active_user)):
    return current_user

@router.get("/verify")
def verify_token(current_user: models.User = Depends(get_current_active_user)):
    return {"valid": True, "user_id": current_user.id}


@users_router.get("/me", response_model=schemas.UserResponse)
def get_user_me(current_user: models.User = Depends(get_current_active_user)):
    return current_user