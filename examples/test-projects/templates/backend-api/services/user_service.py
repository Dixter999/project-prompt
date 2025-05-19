"""
User service functions for authentication and user management
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException
from passlib.context import CryptContext
from typing import Optional

from db import models
from models.user import UserCreate

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hash a password for storage"""
    return pwd_context.hash(password)

def get_user_by_username(db: Session, username: str):
    """Get a user by username"""
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    """Get a user by email"""
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    """Get a user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users_from_db(db: Session, skip: int = 0, limit: int = 100):
    """Get a list of users"""
    return db.query(models.User).offset(skip).limit(limit).all()

def create_new_user(db: Session, user: UserCreate):
    """Create a new user"""
    # Check for existing user with same username or email
    db_user_by_username = get_user_by_username(db, user.username)
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already registered")
        
    db_user_by_email = get_user_by_email(db, user.email)
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    """Authenticate a user by username and password"""
    user = get_user_by_username(db, username)
    
    if not user:
        return None
        
    if not verify_password(password, user.hashed_password):
        return None
        
    return user
