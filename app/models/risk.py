"""
Risk assessment model
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Enum as SQLEnum
from uuid import uuid4
from app.models.base import Base, TimestampMixin
from enum import Enum


class RiskLevel(str, Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskAssessment(Base, TimestampMixin):
    """Risk assessment model"""
    __tablename__ = "risk_assessments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=True)
    address_hash = Column(String(16), nullable=True)
    overall_score = Column(Integer, nullable=False)
    entropy_score = Column(Float, nullable=False)
    uniqueness_score = Column(Float, nullable=False)
    correlation_score = Column(Float, nullable=False)
    temporal_score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    confidence_interval_low = Column(Float, nullable=False)
    confidence_interval_high = Column(Float, nullable=False)
    risk_level = Column(SQLEnum(RiskLevel), nullable=False)
    recommendations = Column(JSON, nullable=False)
    baseline_comparison = Column(JSON, nullable=True)
    assessed_at = Column(DateTime, nullable=False)

    def __repr__(self):
        return f"<RiskAssessment(id={self.id}, overall_score={self.overall_score}, risk_level={self.risk_level})>"
