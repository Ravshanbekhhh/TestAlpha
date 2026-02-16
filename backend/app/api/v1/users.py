"""
User endpoints - student registration and management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse


router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new student user (called from Telegram bot).
    """
    try:
        # Check if user already exists
        stmt = select(User).where(User.telegram_id == user_data.telegram_id)
        result = await db.execute(stmt)
        existing_user = result.scalars().first()
        
        if existing_user:
            return existing_user  # Return existing user if already registered
        
        # Create new user
        user = User(
            telegram_id=user_data.telegram_id,
            full_name=user_data.full_name,
            surname=user_data.surname,
            region=user_data.region
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating user"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID."""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.get("/telegram/{telegram_id}", response_model=UserResponse)
async def get_user_by_telegram_id(
    telegram_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get user by Telegram ID."""
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
