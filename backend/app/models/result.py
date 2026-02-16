"""
Result models - stores test results, MCQ answers, written answers, and reviews.
"""
from sqlalchemy import Column, Integer, Text, Boolean, DateTime, ForeignKey, String
from app.models.types import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Result(Base):
    """Result model - represents a student's test submission."""
    
    __tablename__ = "results"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(), ForeignKey("users.id"), nullable=False)
    test_id = Column(UUID(), ForeignKey("tests.id"), nullable=False)
    session_id = Column(UUID(), ForeignKey("test_sessions.id"), unique=True, nullable=False)
    mcq_score = Column(Integer, default=0, nullable=False)
    written_score = Column(Integer, default=0, nullable=False)
    total_score = Column(Integer, default=0, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="results")
    test = relationship("Test", back_populates="results")
    session = relationship("TestSession", back_populates="result")
    mcq_answers = relationship("MCQAnswer", back_populates="result", cascade="all, delete-orphan")
    written_answers = relationship("WrittenAnswer", back_populates="result", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Result {self.id} - User: {self.user_id}, Score: {self.total_score}>"


class MCQAnswer(Base):
    """MCQ Answer model - stores individual multiple choice answers."""
    
    __tablename__ = "mcq_answers"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    result_id = Column(UUID(), ForeignKey("results.id", ondelete="CASCADE"), nullable=False)
    question_number = Column(Integer, nullable=False)
    student_answer = Column(String(1))  # A, B, C, D, E, or F (or null if not answered)
    correct_answer = Column(String(1), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    
    # Relationships
    result = relationship("Result", back_populates="mcq_answers")
    
    def __repr__(self):
        return f"<MCQAnswer Q{self.question_number}: {self.student_answer} ({'✓' if self.is_correct else '✗'})>"


class WrittenAnswer(Base):
    """Written answer model - stores essay/written answers."""
    
    __tablename__ = "written_answers"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    result_id = Column(UUID(), ForeignKey("results.id", ondelete="CASCADE"), nullable=False)
    question_number = Column(Integer, nullable=False)
    student_answer = Column(Text)
    score = Column(Integer, default=0, nullable=False)
    reviewed_at = Column(DateTime)
    
    # Relationships
    result = relationship("Result", back_populates="written_answers")
    review = relationship("WrittenReview", back_populates="written_answer", uselist=False)
    
    def __repr__(self):
        status = "Reviewed" if self.reviewed_at else "Pending"
        return f"<WrittenAnswer Q{self.question_number} ({status}, Score: {self.score})>"


class WrittenReview(Base):
    """Written review model - stores teacher's review of written answers."""
    
    __tablename__ = "written_reviews"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    written_answer_id = Column(UUID(), ForeignKey("written_answers.id"), unique=True, nullable=False)
    reviewed_by_admin = Column(UUID(), ForeignKey("admin_users.id"), nullable=False)
    score_awarded = Column(Integer, nullable=False)
    comments = Column(Text)
    reviewed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    written_answer = relationship("WrittenAnswer", back_populates="review")
    reviewer = relationship("AdminUser", back_populates="reviews")
    
    def __repr__(self):
        return f"<WrittenReview for Answer {self.written_answer_id}, Score: {self.score_awarded}>"
