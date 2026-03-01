"""
Mock traffic provider for development and testing
"""
import asyncio
import random
from datetime import datetime, timedelta, timezone
from typing import AsyncIterator

from app.services.traffic.base import TrafficProvider, CaptureConfig, CaptureStatus, TrafficRecord


# Common JSON-RPC methods
RPC_METHODS = [
    "eth_getBalance",
    "eth_call",
    "eth_blockNumber",
    "eth_estimateGas",
    "eth_getTransactionCount",
    "eth_chainId",
    "eth_gasPrice",
    "eth_getCode",
    "eth_getStorageAt",
    "eth_getBlockByNumber",
]

# Sample addresses for testing
SAMPLE_ADDRESSES = [
    "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
    "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
    "0x90F79bf6EB2c4f870365E785982E1f101E93b906",
]


class MockTrafficProvider(TrafficProvider):
    """
    Mock traffic provider that generates realistic synthetic traffic patterns.

    Useful for development and testing without requiring actual network capture.
    """

    def __init__(self, count: int = 500):
        self.count = count
        self.active_sessions: dict[str, CaptureConfig] = {}
        self.captured_packets: dict[str, list[TrafficRecord]] = {}

    async def start_capture(self, session_id: str, config: CaptureConfig) -> CaptureStatus:
        """Start mock traffic capture"""
        self.active_sessions[session_id] = config
        self.captured_packets[session_id] = []
        return CaptureStatus(active=True, packets_captured=0)

    async def stop_capture(self, session_id: str) -> CaptureStatus:
        """Stop mock traffic capture"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]

        packets = len(self.captured_packets.get(session_id, []))
        return CaptureStatus(active=False, packets_captured=packets)

    async def get_traffic_stream(self, session_id: str) -> AsyncIterator[TrafficRecord]:
        """Generate and stream mock traffic records"""
        config = self.active_sessions.get(session_id)
        if not config:
            return

        base_time = datetime.now(timezone.utc)
        packet_count = min(self.count, config.packet_count or self.count)

        for i in range(packet_count):
            method = random.choice(RPC_METHODS)
            sample_address = random.choice(SAMPLE_ADDRESSES)

            # Generate request body with address
            request_body = self._generate_request_body(method, sample_address)

            record = TrafficRecord(
                session_id=session_id,
                method="POST",
                endpoint=config.rpc_provider,
                rpc_method=method,
                request_body=request_body,
                request_timestamp=base_time + timedelta(seconds=i * random.random()),
                response_time_ms=random.randint(10, 500),
                response_status=200,
                response_size_bytes=random.randint(100, 5000),
                ip_address=f"192.168.1.{random.randint(1, 255)}",
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            )

            self.captured_packets[session_id].append(record)
            yield record

            # Add small delay to simulate network
            await asyncio.sleep(0.001)

    def _generate_request_body(self, method: str, address: str) -> str:
        """Generate realistic JSON-RPC request body"""
        import json

        params = []
        if "Balance" in method:
            params = [address, "latest"]
        elif "TransactionCount" in method:
            params = [address, "latest"]
        elif "Code" in method:
            params = [address, "latest"]

        return json.dumps({
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": random.randint(1, 1000)
        })
