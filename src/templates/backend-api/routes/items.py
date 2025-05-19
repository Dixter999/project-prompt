"""
Item route handlers for the API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from db import models
from models.item import Item, ItemCreate, ItemUpdate
from middleware.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Create a new item (requires authentication)
    """
    db_item = models.Item(
        title=item.title,
        description=item.description,
        owner_id=current_user.id
    )
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/", response_model=List[Item])
async def read_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get all items (requires authentication)
    """
    items = db.query(models.Item).filter(
        models.Item.owner_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return items

@router.get("/{item_id}", response_model=Item)
async def read_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get item by ID (requires authentication and ownership)
    """
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
        
    if item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this item")
        
    return item

@router.put("/{item_id}", response_model=Item)
async def update_item(
    item_id: int,
    item_data: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Update item (requires authentication and ownership)
    """
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
        
    if db_item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this item")
    
    # Update item fields
    for field, value in item_data.dict(exclude_unset=True).items():
        setattr(db_item, field, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Delete item (requires authentication and ownership)
    """
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
        
    if db_item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this item")
    
    db.delete(db_item)
    db.commit()
    return None
