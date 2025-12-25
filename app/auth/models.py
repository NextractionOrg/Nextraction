from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class User(BaseModel):
    """User model"""
    id: str
    username: str
    email: EmailStr
    hashed_password: str
    created_at: datetime
    is_active: bool = True


class UserCreate(BaseModel):
    """User creation model"""
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response model (without password)"""
    id: str
    username: str
    email: EmailStr
    created_at: datetime
    is_active: bool


class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data model"""
    username: Optional[str] = None
    user_id: Optional[str] = None

