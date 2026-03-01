"""
Base interface for traffic capture providers
"""
from abc import ABC, abstractmethod
from typing import AsyncIterator
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CaptureConfig:
    """Configuration for traffic capture"""
    wallet_type: str
    rpc_provider: str
    duration_seconds: int | None = None
    packet_count: int | None = None
    address_hashes: list[str] | None = None


@dataclass
class CaptureStatus:
    """Status of traffic capture"""
    active: bool
    packets_captured: int
    error: str | None = None


@dataclass
class TrafficRecord:
    """Single traffic record"""
    session_id: str
    method: str
    endpoint: str
    rpc_method: str | None = None
    request_body: str | None = None
    request_timestamp: datetime | None = None
    response_time_ms: int | None = None
    response_status: int | None = None
    response_size_bytes: int | None = None
    ip_address: str | None = None
    user_agent: str | None = None


class TrafficProvider(ABC):
    """Abstract base class for traffic capture providers"""

    @abstractmethod
    async def start_capture(self, session_id: str, config: CaptureConfig) -> CaptureStatus:
        """Start traffic capture for a session"""
        pass

    @abstractmethod
    async def stop_capture(self, session_id: str) -> CaptureStatus:
        """Stop traffic capture"""
        pass

    @abstractmethod
    async def get_traffic_stream(self, session_id: str) -> AsyncIterator[TrafficRecord]:
        """Stream captured traffic records"""
        pass
