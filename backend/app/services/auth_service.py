"""
Authentication service for admin users.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from uuid import UUID

from app.models.admin import AdminUser
from app.schemas.admin import AdminCreate, AdminLogin, Token, TokenData
from app.utils.security import verify_password, get_password_hash, create_access_token


async def create_admin(db: AsyncSession, admin_data: AdminCreate) -> AdminUser:
    """
    Create a new admin user.
    
    Args:
        db: Database session
        admin_data: Admin creation data
    
    Returns:
        Created AdminUser instance
    """
    hashed_password = get_password_hash(admin_data.password)
    
    admin = AdminUser(
        username=admin_data.username,
        password_hash=hashed_password,
        role=admin_data.role
    )
    
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    
    return admin


async def authenticate_admin(db: AsyncSession, login_data: AdminLogin) -> Optional[AdminUser]:
    """
    Authenticate admin user with username and password.
    
    Args:
        db: Database session
        login_data: Login credentials
    
    Returns:
        AdminUser if authenticated, None otherwise
    """
    stmt = select(AdminUser).where(AdminUser.username == login_data.username)
    result = await db.execute(stmt)
    admin = result.scalars().first()
    
    if not admin:
        return None
    
    if not verify_password(login_data.password, admin.password_hash):
        return None
    
    return admin


async def get_admin_by_id(db: AsyncSession, admin_id: UUID) -> Optional[AdminUser]:
    """
    Get admin user by ID.
    
    Args:
        db: Database session
        admin_id: Admin UUID
    
    Returns:
        AdminUser if found, None otherwise
    """
    stmt = select(AdminUser).where(AdminUser.id == admin_id)
    result = await db.execute(stmt)
    return result.scalars().first()


def create_admin_token(admin: AdminUser) -> Token:
    """
    Create JWT token for admin user.
    
    Args:
        admin: AdminUser instance
    
    Returns:
        Token with access_token and token_type
    """
    token_data = {
        "sub": str(admin.id),
        "username": admin.username,
        "role": admin.role
    }
    access_token = create_access_token(token_data)
    
    return Token(access_token=access_token, token_type="bearer")
