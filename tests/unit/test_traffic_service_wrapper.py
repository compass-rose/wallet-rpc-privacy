"""
Unit tests for traffic service wrapper
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.traffic_service import TrafficService
from app.services.traffic.base import TrafficProvider, CaptureConfig, TrafficRecord, CaptureStatus
from app.models import NetworkTraffic
from app.services.traffic_service import TrafficService
from app.services.traffic.base import TrafficProvider, CaptureConfig, TrafficRecord, CaptureStatus
from app.models import NetworkTraffic


class TestTrafficService:
    """Test TrafficService class"""

    @pytest.fixture
    def mock_provider(self):
        """Create mock traffic provider"""
        provider = Mock(spec=TrafficProvider)
        provider.start_capture = AsyncMock()
        provider.stop_capture = AsyncMock()
        provider.get_traffic_stream = MagicMock()
        return provider

    @pytest.fixture
    def traffic_service(self, mock_provider):
        """Create traffic service instance with mock provider"""
        return TrafficService(provider=mock_provider)

    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        db = Mock(spec=AsyncSession)
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        db.add = Mock()
        return db

    @pytest.fixture
    def sample_config(self):
        """Create sample capture config"""
        return CaptureConfig(
            wallet_type="MetaMask",
            rpc_provider="https://mainnet.infura.io/v3/test",
            packet_count=10
        )

    @pytest.fixture
    def sample_traffic_record(self):
        """Create sample traffic record"""
        return TrafficRecord(
            session_id="test-session-1",
            method="POST",
            endpoint="/rpc",
            rpc_method="eth_getBalance",
            request_body='{"jsonrpc":"2.0","method":"eth_getBalance"}',
            request_timestamp=datetime.now(timezone.utc),
            response_time_ms=100,
            response_status=200,
            response_size_bytes=500,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )

    @pytest.mark.asyncio
    async def test_traffic_service_initialization(self, mock_provider):
        """Test that TrafficService initializes with provider"""
        service = TrafficService(provider=mock_provider)
        assert service.provider == mock_provider

    @pytest.mark.asyncio
    async def test_start_capture_success(self, traffic_service, sample_config):
        """Test starting traffic capture successfully"""
        session_id = "test-session-1"
        mock_status = CaptureStatus(active=True, packets_captured=0, error=None)
        traffic_service.provider.start_capture.return_value = mock_status

        result = await traffic_service.start_capture(session_id, sample_config)

        assert result["active"] is True
        assert result["packets_captured"] == 0
        traffic_service.provider.start_capture.assert_called_once_with(session_id, sample_config)

    @pytest.mark.asyncio
    async def test_start_capture_with_packets(self, traffic_service, sample_config):
        """Test starting capture with initial packets captured"""
        session_id = "test-session-1"
        mock_status = CaptureStatus(active=True, packets_captured=5, error=None)
        traffic_service.provider.start_capture.return_value = mock_status

        result = await traffic_service.start_capture(session_id, sample_config)

        assert result["active"] is True
        assert result["packets_captured"] == 5

    @pytest.mark.asyncio
    async def test_stop_capture_success(self, traffic_service):
        """Test stopping traffic capture successfully"""
        session_id = "test-session-1"
        mock_status = CaptureStatus(active=False, packets_captured=10, error=None)
        traffic_service.provider.stop_capture.return_value = mock_status

        result = await traffic_service.stop_capture(session_id)

        assert result["active"] is False
        assert result["packets_captured"] == 10
        assert result["error"] is None
        traffic_service.provider.stop_capture.assert_called_once_with(session_id)

    @pytest.mark.asyncio
    async def test_stop_capture_with_error(self, traffic_service):
        """Test stopping capture with error status"""
        session_id = "test-session-1"
        mock_status = CaptureStatus(
            active=False,
            packets_captured=5,
            error="ConnectionLost"
        )
        traffic_service.provider.stop_capture.return_value = mock_status

        result = await traffic_service.stop_capture(session_id)

        assert result["active"] is False
        assert result["packets_captured"] == 5
        assert result["error"] == "ConnectionLost"

    @pytest.mark.asyncio
    async def test_process_and_store_success(
        self, traffic_service, mock_db, sample_traffic_record
    ):
        """Test processing and storing traffic record"""
        session_id = "test-session-1"

        # Mock hash_ip utility
        with patch('app.services.traffic_service.hash_ip') as mock_hash:
            mock_hash.return_value = "hashed_ip_123"

            result = await traffic_service.process_and_store(
                session_id,
                sample_traffic_record,
                mock_db
            )

            assert result.session_id == session_id
            assert result.method == "POST"
            assert result.rpc_method == "eth_getBalance"
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(result)
            mock_hash.assert_called_once_with("192.168.1.1")

    @pytest.mark.asyncio
    async def test_process_and_store_without_ip(
        self, traffic_service, mock_db, sample_traffic_record
    ):
        """Test processing record without IP address"""
        session_id = "test-session-1"
        record = sample_traffic_record
        record.ip_address = None

        with patch('app.services.traffic_service.hash_ip') as mock_hash:
            result = await traffic_service.process_and_store(
                session_id,
                record,
                mock_db
            )

            assert result.ip_address_hash is None
            mock_hash.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_and_store_multiple_records(
        self, traffic_service, mock_db, sample_traffic_record
    ):
        """Test processing multiple records sequentially"""
        session_id = "test-session-1"

        with patch('app.services.traffic_service.hash_ip') as mock_hash:
            mock_hash.return_value = "hashed_ip_123"

            for i in range(3):
                record = sample_traffic_record
                result = await traffic_service.process_and_store(
                    session_id,
                    record,
                    mock_db
                )

                assert mock_db.add.call_count == i + 1
                assert mock_db.commit.call_count == i + 1

    @pytest.mark.asyncio
    async def test_stream_and_store_empty_stream(self, traffic_service, mock_db):
        """Test streaming when provider returns no records"""
        session_id = "test-session-1"
        async def async_gen(sid):
            return
            yield  # This makes it an async generator with no yields

        traffic_service.provider.get_traffic_stream = async_gen

        count = await traffic_service.stream_and_store(session_id, mock_db)

        assert count == 0
        mock_db.add.assert_not_called()
        mock_db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_stream_and_store_single_record(
        self, traffic_service, mock_db, sample_traffic_record
    ):
        """Test streaming and storing a single record"""
        session_id = "test-session-1"

        # Create async generator
        async def async_gen(sid):
            yield sample_traffic_record

        traffic_service.provider.get_traffic_stream = async_gen

        with patch('app.services.traffic_service.hash_ip') as mock_hash:
            mock_hash.return_value = "hashed_ip_123"

            count = await traffic_service.stream_and_store(session_id, mock_db)

            assert count == 1
            assert mock_db.add.call_count == 1
            assert mock_db.commit.call_count == 1

    @pytest.mark.asyncio
    async def test_stream_and_store_multiple_records(
        self, traffic_service, mock_db, sample_traffic_record
    ):
        """Test streaming and storing multiple records"""
        session_id = "test-session-1"
        num_records = 5

        # Create async generator with multiple records
        async def async_gen(sid):
            for i in range(num_records):
                record = sample_traffic_record
                record.rpc_method = f"eth_method_{i}"
                yield record

        traffic_service.provider.get_traffic_stream = async_gen

        with patch('app.services.traffic_service.hash_ip') as mock_hash:
            mock_hash.return_value = "hashed_ip_123"

            count = await traffic_service.stream_and_store(session_id, mock_db)

            assert count == num_records
            assert mock_db.add.call_count == num_records
            assert mock_db.commit.call_count == num_records

    @pytest.mark.asyncio
    async def test_capture_workflow_lifecycle(
        self, traffic_service, sample_config, sample_traffic_record
    ):
        """Test full lifecycle: start capture -> stream -> stop capture"""
        session_id = "test-session-1"
        mock_db = Mock(spec=AsyncSession)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        mock_db.add = Mock()

        # Start capture
        mock_start_status = CaptureStatus(active=True, packets_captured=0, error=None)
        traffic_service.provider.start_capture.return_value = mock_start_status

        start_result = await traffic_service.start_capture(session_id, sample_config)
        assert start_result["active"] is True

        # Stream records
        async def stream_gen(sid):
            yield sample_traffic_record

        traffic_service.provider.get_traffic_stream = stream_gen

        with patch('app.services.traffic_service.hash_ip') as mock_hash:
            mock_hash.return_value = "hashed"
            stream_count = await traffic_service.stream_and_store(session_id, mock_db)

        assert stream_count == 1

        # Stop capture
        mock_stop_status = CaptureStatus(active=False, packets_captured=1, error=None)
        traffic_service.provider.stop_capture.return_value = mock_stop_status

        stop_result = await traffic_service.stop_capture(session_id)
        assert stop_result["active"] is False
        assert stop_result["packets_captured"] == 1

    @pytest.mark.asyncio
    async def test_concurrent_sessions(self, traffic_service, sample_config):
        """Test handling multiple concurrent sessions"""
        session_1 = "session-1"
        session_2 = "session-2"

        mock_status = CaptureStatus(active=True, packets_captured=0, error=None)
        traffic_service.provider.start_capture.return_value = mock_status

        # Start both sessions
        result_1 = await traffic_service.start_capture(session_1, sample_config)
        result_2 = await traffic_service.start_capture(session_2, sample_config)

        assert result_1["active"] is True
        assert result_2["active"] is True
        assert traffic_service.provider.start_capture.call_count == 2
