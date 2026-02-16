"""
Admin and authentication schemas.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class AdminCreate(BaseModel):
    """Schema for creating admin user."""
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)
    role: str = Field(default="teacher")


class AdminLogin(BaseModel):
    """Schema for admin login."""
    username: str
    password: str


class AdminResponse(BaseModel):
    """Schema for admin response."""
    id: UUID
    username: str
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data."""
    admin_id: UUID
    username: str
    role: str
