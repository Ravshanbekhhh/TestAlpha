"""
Test session model - tracks student test-taking sessions with timers.
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, UniqueConstraint, Integer
from app.models.types import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import uuid

from app.database import Base
from app.utils.timer import now_uz


class TestSession(Base):
    """Test session model - represents a student's test-taking session."""
    
    __tablename__ = "test_sessions"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(), ForeignKey("users.id"), nullable=False)
    test_id = Column(UUID(), ForeignKey("tests.id"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    started_at = Column(DateTime, default=now_uz, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_submitted = Column(Boolean, default=False, nullable=False)
    is_expired = Column(Boolean, default=False, nullable=False)
    extra_minutes = Column(Integer, default=0, nullable=False)  # Admin qo'shgan daqiqalar (max 15)
    
    # Unique constraint to prevent multiple attempts
    __table_args__ = (
        UniqueConstraint('user_id', 'test_id', name='uq_user_test_attempt'),
    )
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    test = relationship("Test", back_populates="sessions")
    result = relationship("Result", back_populates="session", uselist=False)
    
    @property
    def is_valid(self) -> bool:
        """Check if session is still valid."""
        return not self.is_expired and not self.is_submitted and now_uz() < self.expires_at
    
    @property
    def time_remaining_seconds(self) -> int:
        """Get remaining time in seconds."""
        if self.is_expired or self.is_submitted:
            return 0
        remaining = (self.expires_at - now_uz()).total_seconds()
        return max(0, int(remaining))
    
    def __repr__(self):
        return f"<TestSession {self.session_token} (User: {self.user_id}, Test: {self.test_id})>"
