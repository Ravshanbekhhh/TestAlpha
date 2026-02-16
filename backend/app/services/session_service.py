"""
Session management service for test-taking sessions.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.models.session import TestSession
from app.models.user import User
from app.models.test import Test
from app.utils.timer import generate_session_token, calculate_expiry_time
from app.config import settings


async def create_session(db: AsyncSession, user_id: UUID, test_id: UUID) -> Optional[TestSession]:
    """
    Create a new test session for a user.
    Prevents multiple attempts (unique constraint on user_id + test_id).
    
    Args:
        db: Database session
        user_id: User UUID
        test_id: Test UUID
    
    Returns:
        TestSession if created, None if user already attempted this test
    """
    try:
        session_token = generate_session_token()
        expires_at = calculate_expiry_time(settings.SESSION_DURATION_MINUTES)
        
        session = TestSession(
            user_id=user_id,
            test_id=test_id,
            session_token=session_token,
            started_at=datetime.utcnow(),
            expires_at=expires_at,
            is_submitted=False,
            is_expired=False
        )
        
        db.add(session)
        await db.commit()
        await db.refresh(session)
        
        return session
    except IntegrityError:
        # User already has a session for this test
        await db.rollback()
        return None


async def get_session_by_token(db: AsyncSession, session_token: str) -> Optional[TestSession]:
    """
    Get session by token.
    
    Args:
        db: Database session
        session_token: Session token string
    
    Returns:
        TestSession if found, None otherwise
    """
    stmt = select(TestSession).where(TestSession.session_token == session_token)
    result = await db.execute(stmt)
    session = result.scalars().first()
    
    # Auto-expire if time has passed
    if session and not session.is_submitted and not session.is_expired:
        if datetime.utcnow() >= session.expires_at:
            session.is_expired = True
            await db.commit()
    
    return session


async def mark_session_submitted(db: AsyncSession, session_id: UUID) -> Optional[TestSession]:
    """
    Mark session as submitted.
    
    Args:
        db: Database session
        session_id: Session UUID
    
    Returns:
        Updated TestSession if found, None otherwise
    """
    stmt = select(TestSession).where(TestSession.id == session_id)
    result = await db.execute(stmt)
    session = result.scalars().first()
    
    if session:
        session.is_submitted = True
        await db.commit()
        await db.refresh(session)
    
    return session


async def check_user_attempted_test(db: AsyncSession, user_id: UUID, test_id: UUID) -> bool:
    """
    Check if user has already attempted this test.
    
    Args:
        db: Database session
        user_id: User UUID
        test_id: Test UUID
    
    Returns:
        True if attempted, False otherwise
    """
    stmt = select(TestSession).where(
        TestSession.user_id == user_id,
        TestSession.test_id == test_id
    )
    result = await db.execute(stmt)
    session = result.scalars().first()
    
    return session is not None
