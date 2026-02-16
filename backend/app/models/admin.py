"""
Admin user model for system administrators.
"""
from sqlalchemy import Column, String, DateTime, func
from app.models.types import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class AdminUser(Base):
    """Admin/Teacher user model."""
    
    __tablename__ = "admin_users"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="teacher", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    tests_created = relationship("Test", back_populates="creator", cascade="all, delete-orphan")
    reviews = relationship("WrittenReview", back_populates="reviewer")
    
    def __repr__(self):
        return f"<AdminUser {self.username} ({self.role})>"
