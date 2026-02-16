"""
User model for student/test taker.
"""
from sqlalchemy import Column, BigInteger, String, DateTime, func
from app.models.types import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class User(Base):
    """Student user model."""
    
    __tablename__ = "users"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    surname = Column(String(255), nullable=False)
    region = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    sessions = relationship("TestSession", back_populates="user", cascade="all, delete-orphan")
    results = relationship("Result", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.full_name} {self.surname} (TG: {self.telegram_id})>"
