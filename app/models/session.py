"""
Session model for capture sessions
"""
from sqlalchemy import Column, String, Integer, JSON, Enum as SQLEnum, DateTime
from uuid import uuid4
from enum import Enum
from app.models.base import Base, TimestampMixin


class SessionStatus(str, Enum):
    """Session status enumeration"""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


class Session(Base, TimestampMixin):
    """Capture session model"""
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    wallet_type = Column(String(255), nullable=False)
    rpc_provider = Column(String(255), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    packet_count = Column(Integer, default=0, nullable=False)
    duration_seconds = Column(Integer, nullable=True)
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.ACTIVE, nullable=False)
    session_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata'

    def __repr__(self):
        return f"<Session(id={self.id}, wallet_type={self.wallet_type}, status={self.status})>"
