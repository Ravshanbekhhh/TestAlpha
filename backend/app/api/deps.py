"""
API dependencies - authentication and database session injection.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

from app.database import get_db
from app.utils.security import decode_access_token
from app.services.auth_service import get_admin_by_id
from app.models.admin import AdminUser
from app.schemas.admin import TokenData


# HTTP Bearer scheme for JWT
security = HTTPBearer()


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> AdminUser:
    """
    Dependency to get current authenticated admin user.
    Validates JWT token and retrieves admin from database.
    
    Raises:
        HTTPException: If token is invalid or admin not found
    """
    token = credentials.credentials
    token_data = decode_access_token(token)
    
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    admin = await get_admin_by_id(db, token_data.admin_id)
    
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin user not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return admin
