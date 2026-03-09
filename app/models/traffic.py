"""
Network traffic model
"""
from sqlalchemy import Column, String, Integer, BigInteger, DateTime, ForeignKey, Text
from uuid import uuid4
from app.models.base import Base, TimestampMixin
from sqlalchemy.orm import relationship


class NetworkTraffic(Base, TimestampMixin):
    """Network traffic record model"""
    __tablename__ = "network_traffic"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    method = Column(String(16), nullable=False)  # HTTP method
    endpoint = Column(String(2048), nullable=False)
    request_body = Column(Text, nullable=True)  # Anonymized
    rpc_method = Column(String(255), nullable=True)
    rpc_params_hash = Column(String(64), nullable=True)
    request_timestamp = Column(DateTime, nullable=False)
    response_time_ms = Column(Integer, nullable=True)
    response_status = Column(Integer, nullable=True)
    response_size_bytes = Column(BigInteger, nullable=True)
    ip_address_hash = Column(String(64), nullable=True)
    address_hash = Column(String(64), nullable=True)  # Hashed wallet address
    user_agent = Column(String(512), nullable=True)

    session = relationship("Session", backref="traffic")

    def __repr__(self):
        return f"<NetworkTraffic(id={self.id}, session_id={self.session_id}, rpc_method={self.rpc_method})>"
