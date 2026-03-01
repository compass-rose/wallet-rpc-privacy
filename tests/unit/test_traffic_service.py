"""
Unit tests for traffic capture service
"""
import pytest
from app.services.traffic.mock_provider import MockTrafficProvider
from app.services.traffic.base import CaptureConfig


@pytest.mark.asyncio
async def test_mock_provider_starts_capture():
    """Test that mock provider can start capture"""
    provider = MockTrafficProvider(count=100)
    config = CaptureConfig(
        wallet_type="MetaMask",
        rpc_provider="https://mainnet.infura.io/v3/test"
    )

    status = await provider.start_capture("test-session", config)

    assert status.active is True
    assert status.packets_captured == 0


@pytest.mark.asyncio
async def test_mock_provider_stops_capture():
    """Test that mock provider can stop capture"""
    provider = MockTrafficProvider(count=100)
    config = CaptureConfig(wallet_type="MetaMask", rpc_provider="https://mainnet.infura.io/v3/test")

    await provider.start_capture("test-session", config)
    status = await provider.stop_capture("test-session")

    assert status.active is False


@pytest.mark.asyncio
async def test_mock_provider_generates_traffic():
    """Test that mock provider generates traffic records"""
    provider = MockTrafficProvider(count=10)
    config = CaptureConfig(
        wallet_type="MetaMask",
        rpc_provider="https://mainnet.infura.io/v3/test",
        packet_count=10
    )

    await provider.start_capture("test-session", config)

    count = 0
    async for record in provider.get_traffic_stream("test-session"):
        assert record.session_id == "test-session"
        assert record.method == "POST"
        assert record.rpc_method is not None
        assert record.response_status == 200
        count += 1

    assert count == 10


@pytest.mark.asyncio
async def test_traffic_factory():
    """Test traffic provider factory"""
    from app.services.traffic.factory import get_traffic_provider

    provider = get_traffic_provider("mock", count=50)
    assert isinstance(provider, MockTrafficProvider)


@pytest.mark.asyncio
async def test_traffic_factory_invalid_type():
    """Test that factory raises error for invalid provider type"""
    from app.services.traffic.factory import get_traffic_provider

    with pytest.raises(ValueError) as exc_info:
        get_traffic_provider("invalid")

    assert "Unknown provider type" in str(exc_info.value)
