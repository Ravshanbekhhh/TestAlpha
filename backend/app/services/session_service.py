"""
Session management service for test-taking sessions.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta

from app.models.session import TestSession
from app.models.user import User
from app.models.test import Test
from app.utils.timer import generate_session_token
from app.config import settings


async def create_session(db: AsyncSession, user_id: UUID, test_id: UUID) -> Optional[TestSession]:
    """
    Create a new test session for a user.
    Uses test's end_time + extra_minutes as session expiry if set,
    otherwise falls back to SESSION_DURATION_MINUTES.
    """
    try:
        # Load test to get time settings
        stmt = select(Test).where(Test.id == test_id)
        result = await db.execute(stmt)
        test = result.scalars().first()
        
        if not test:
            return None
        
        # Delete any old unsubmitted sessions for this user+test
        # (allows retry if previous session expired without submitting)
        from sqlalchemy import delete, and_
        cleanup_stmt = delete(TestSession).where(
            and_(
                TestSession.user_id == user_id,
                TestSession.test_id == test_id,
                TestSession.is_submitted == False
            )
        )
        await db.execute(cleanup_stmt)
        
        now = datetime.utcnow()
        
        # Check time window if test has scheduled times
        if test.start_time and now < test.start_time:
            raise ValueError("TEST_NOT_STARTED")
        
        if test.end_time:
            effective_end = test.end_time + timedelta(minutes=test.extra_minutes)
            if now >= effective_end:
                raise ValueError("TEST_ENDED")
            # Session expires at test end_time + extra_minutes
            expires_at = effective_end
        else:
            # No scheduled end time - use default duration
            expires_at = now + timedelta(minutes=settings.SESSION_DURATION_MINUTES)
        
        session_token = generate_session_token()
        
        session = TestSession(
            user_id=user_id,
            test_id=test_id,
            session_token=session_token,
            started_at=now,
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
    """Get session by token."""
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
    """Mark session as submitted."""
    stmt = select(TestSession).where(TestSession.id == session_id)
    result = await db.execute(stmt)
    session = result.scalars().first()
    
    if session:
        session.is_submitted = True
        await db.commit()
        await db.refresh(session)
    
    return session


async def check_user_attempted_test(db: AsyncSession, user_id: UUID, test_id: UUID) -> bool:
    """Check if user has already submitted this test (only counts submitted sessions)."""
    stmt = select(TestSession).where(
        TestSession.user_id == user_id,
        TestSession.test_id == test_id,
        TestSession.is_submitted == True
    )
    result = await db.execute(stmt)
    session = result.scalars().first()
    
    return session is not None


async def extend_session(db: AsyncSession, session_id: UUID, minutes: int = 5) -> Optional[TestSession]:
    """
    Extend a specific session by adding minutes.
    Max 3 extensions (15 minutes total per session).
    """
    stmt = select(TestSession).where(TestSession.id == session_id)
    result = await db.execute(stmt)
    session = result.scalars().first()
    
    if not session:
        return None
    
    if session.is_submitted:
        raise ValueError("SESSION_ALREADY_SUBMITTED")
    
    if session.extra_minutes >= 15:
        raise ValueError("MAX_EXTENSIONS_REACHED")
    
    session.extra_minutes += minutes
    session.expires_at = session.expires_at + timedelta(minutes=minutes)
    await db.commit()
    await db.refresh(session)
    
    return session
