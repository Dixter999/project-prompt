"""
Item data models for request/response validation
"""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ItemBase(BaseModel):
    """Base item model with common attributes"""
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)

class ItemCreate(ItemBase):
    """Item creation model"""
    pass

class ItemUpdate(ItemBase):
    """Item update model with optional fields"""
    title: Optional[str] = Field(None, min_length=1, max_length=100)

class Item(ItemBase):
    """Item response model with additional database fields"""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
