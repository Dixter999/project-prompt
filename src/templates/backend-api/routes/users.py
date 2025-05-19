"""
User route handler for the API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from db import models
from models.user import UserCreate, User, UserUpdate
from middleware.auth import get_current_user
from services.user_service import create_new_user, get_users_from_db, get_user_by_id

router = APIRouter()

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user
    """
    return create_new_user(db, user)

@router.get("/", response_model=List[User])
async def get_users(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get all users (requires authentication)
    """
    return get_users_from_db(db, skip, limit)

@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get user by ID (requires authentication)
    """
    db_user = get_user_by_id(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Update user information (requires authentication and ownership)
    """
    db_user = get_user_by_id(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
        
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403, 
            detail="Not authorized to update this user"
        )
        
    # Update user fields
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user
