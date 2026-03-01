"""
Privacy leak events and detection rules models
"""
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum
from uuid import uuid4
from app.models.base import Base, TimestampMixin
from enum import Enum


class LeakType(str, Enum):
    """Privacy leak type enumeration"""
    IDENTITY = "identity"
    ASSET = "asset"
    BEHAVIOR = "behavior"
    LOCATION = "location"


class Priority(str, Enum):
    """Rule priority enumeration"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PrivacyLeakEvent(Base, TimestampMixin):
    """Privacy leak event model"""
    __tablename__ = "privacy_leak_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    leak_type = Column(SQLEnum(LeakType), nullable=False)
    method_name = Column(String(255), nullable=False)
    description = Column(String(2048), nullable=False)
    confidence = Column(Float, nullable=False)
    confidence_interval_low = Column(Float, nullable=False)
    confidence_interval_high = Column(Float, nullable=False)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, nullable=False)
    address_hash = Column(String(16), nullable=False)
    rule_id = Column(String(64), nullable=False)

    def __repr__(self):
        return f"<PrivacyLeakEvent(id={self.id}, leak_type={self.leak_type}, confidence={self.confidence})>"


class DetectionRule(Base, TimestampMixin):
    """Detection rule model"""
    __tablename__ = "detection_rules"

    id = Column(String(64), primary_key=True)
    name = Column(String(255), nullable=False)
    category = Column(SQLEnum(LeakType), nullable=False)
    description = Column(String(2048), nullable=False)  # Fixed length for MySQL VARCHAR
    conditions = Column(JSON, nullable=False)
    actions = Column(JSON, nullable=False)
    priority = Column(SQLEnum(Priority), default=Priority.MEDIUM, nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    version = Column(Integer, default=1, nullable=False)

    def __repr__(self):
        return f"<DetectionRule(id={self.id}, name={self.name}, enabled={self.enabled})>"
