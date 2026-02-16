"""
User schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class UserCreate(BaseModel):
    """Schema for creating a new user (from Telegram bot)."""
    telegram_id: int = Field(..., description="Telegram user ID")
    full_name: str = Field(..., min_length=1, max_length=255)
    surname: str = Field(..., min_length=1, max_length=255)
    region: str = Field(..., min_length=1, max_length=255)


class UserResponse(BaseModel):
    """Schema for user response."""
    id: UUID
    telegram_id: int
    full_name: str
    surname: str
    region: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user info."""
    full_name: str | None = None
    surname: str | None = None
    region: str | None = None
