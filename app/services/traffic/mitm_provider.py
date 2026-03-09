"""
Mitmproxy traffic provider - Reserved for real data capture

This provider interfaces with mitmproxy for actual TLS interception
and network traffic capture from real wallet applications.
"""
import asyncio
from typing import AsyncIterator

from app.services.traffic.base import TrafficProvider, CaptureConfig, CaptureStatus, TrafficRecord


class MitmTrafficProvider(TrafficProvider):
    """
    Real traffic capture via mitmproxy.

    RESERVED FOR PRODUCTION USE - Requires:
    1. CA certificate installation
    2. Wallet proxy configuration
    3. PCAP encryption setup
    4. mitmproxy addon for JSON-RPC parsing

    See user manual for full setup instructions.
    """

    def __init__(self):
        self.active_sessions: dict[str, CaptureConfig] = {}
        self.captured_packets: dict[str, list[TrafficRecord]] = {}

    async def start_capture(self, session_id: str, config: CaptureConfig) -> CaptureStatus:
        """
        Start real traffic capture via mitmproxy.

        TODO: Implement:
        1. Start mitmproxy instance in reverse mode
        2. Configure TLS interception
        3. Set up PCAP file storage (encrypted)
        """
        raise NotImplementedError(
            "Mitm provider requires TLS certificate setup. "
            "See user manual for production configuration."
        )

    async def stop_capture(self, session_id: str) -> CaptureStatus:
        """
        Stop real traffic capture.

        TODO: Implement:
        1. Stop mitmproxy instance
        2. Finalize PCAP file
        3. Return packet counts
        """
        raise NotImplementedError(
            "Mitm provider requires TLS certificate setup. "
            "See user manual for production configuration."
        )

    async def get_traffic_stream(self, session_id: str) -> AsyncIterator[TrafficRecord]:
        """
        Stream real traffic from PCAP files.

        TODO: Implement:
        1. Parse PCAP files with scapy
        2. Extract JSON-RPC payloads
        3. anonymize sensitive data
        4. Yield TrafficRecord objects
        """
        raise NotImplementedError(
            "Mitm provider requires TLS certificate setup. "
            "See user manual for production configuration."
        )
