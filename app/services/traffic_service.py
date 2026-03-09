"""
Traffic capture service - high-level interface
"""
import hashlib
import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.traffic.base import TrafficProvider, CaptureConfig, TrafficRecord
from app.services.traffic.factory import get_traffic_provider
from app.models import NetworkTraffic
from app.utils import hash_ip


class TrafficService:
    """Service for managing traffic capture and processing"""

    def __init__(self, provider: TrafficProvider):
        self.provider = provider

    async def start_capture(self, session_id: str, config: CaptureConfig) -> dict:
        """
        Start traffic capture for a session

        Args:
            session_id: Session UUID
            config: Capture configuration

        Returns:
            Dictionary with capture status
        """
        status = await self.provider.start_capture(session_id, config)
        return {
            "active": status.active,
            "packets_captured": status.packets_captured
        }

    async def stop_capture(self, session_id: str) -> dict:
        """
        Stop traffic capture for a session

        Args:
            session_id: Session UUID

        Returns:
            Dictionary with final capture status
        """
        status = await self.provider.stop_capture(session_id)
        return {
            "active": status.active,
            "packets_captured": status.packets_captured,
            "error": status.error
        }

    async def process_and_store(
        self,
        session_id: str,
        record: TrafficRecord,
        db: AsyncSession
    ) -> NetworkTraffic:
        """
        Process a traffic record and store in database

        Args:
            session_id: Session UUID
            record: Traffic record to process
            db: Database session

        Returns:
            Created NetworkTraffic model
        """
        # Extract and hash wallet address from request_body
        address_hash = None
        if record.request_body and record.rpc_method:
            try:
                body = json.loads(record.request_body)
                params = body.get("params", [])
                if params and isinstance(params[0], str) and params[0].startswith("0x"):
                    address_hash = hashlib.sha256(params[0].encode()).hexdigest()
            except (json.JSONDecodeError, IndexError, KeyError):
                pass

        traffic = NetworkTraffic(
            session_id=session_id,
            method=record.method,
            endpoint=record.endpoint,
            rpc_method=record.rpc_method,
            request_body=record.request_body,
            request_timestamp=record.request_timestamp,
            response_time_ms=record.response_time_ms,
            response_status=record.response_status,
            response_size_bytes=record.response_size_bytes,
            ip_address_hash=hash_ip(record.ip_address) if record.ip_address else None,
            address_hash=address_hash,
            user_agent=record.user_agent
        )

        db.add(traffic)
        await db.commit()
        await db.refresh(traffic)

        return traffic

    async def stream_and_store(self, session_id: str, db: AsyncSession) -> int:
        """
        Stream traffic records from provider and store in database

        Args:
            session_id: Session UUID
            db: Database session

        Returns:
            Number of records stored
        """
        count = 0
        async for record in self.provider.get_traffic_stream(session_id):
            await self.process_and_store(session_id, record, db)
            count += 1

        return count
