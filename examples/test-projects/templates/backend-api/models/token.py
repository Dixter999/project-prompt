"""
Token data models for authentication
"""
from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    """Token model returned during authentication"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Token data model for internal use"""
    username: Optional[str] = None
