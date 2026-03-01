"""
Unit tests for detection service
"""
import pytest
from unittest.mock import Mock, AsyncMock
from app.services.detection_service import DetectionService


class TestDetectionService:
    """Test DetectionService class"""

    @pytest.fixture
    def detection_service(self):
        """Create detection service instance"""
        return DetectionService()

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test that detection service initializes correctly"""
        service = DetectionService()
        assert service.engine is not None
        assert hasattr(service, "engine")

    @pytest.mark.asyncio
    async def test_run_detection_with_empty_traffic(self):
        """Test detection with empty traffic records"""
        service = DetectionService()
        session_id = "test-session"
        traffic_records = []

        events = await service.run_detection(session_id, traffic_records)

        assert isinstance(events, list)

    @pytest.mark.asyncio
    async def test_get_rules(self):
        """Test getting all detection rules"""
        service = DetectionService()
        rules = service.get_rules()

        assert isinstance(rules, list)

    @pytest.mark.asyncio
    async def test_get_rules_summary(self):
        """Test getting rules summary statistics"""
        service = DetectionService()
        summary = service.get_rules_summary()

        assert isinstance(summary, dict)

    @pytest.mark.asyncio
    async def test_store_events_with_mock_db(self, detection_service):
        """Test storing events with mock database session"""
        from app.models import PrivacyLeakEvent

        # Create mock events
        mock_events = [
            PrivacyLeakEvent(
                id="1",
                session_id="session-1",
                leak_type="identity",
                method_name="POST",
                description="Test leak",
                confidence=0.9,
                details={},
                timestamp="2024-01-01T00:00:00",
                address_hash="abc12345",
                rule_id="DR-ID-1"
            )
        ]

        # Create mock database session
        mock_db = Mock()
        mock_db.commit = AsyncMock()
        mock_db.add = Mock()

        # Store events
        count = await detection_service.store_events(mock_events, mock_db)

        assert count == 1
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_store_multiple_events(self, detection_service):
        """Test storing multiple events"""
        from app.models import PrivacyLeakEvent

        # Create mock events
        mock_events = [
            PrivacyLeakEvent(
                id=str(i),
                session_id="session-1",
                leak_type="identity",
                method_name="POST",
                description=f"Test leak {i}",
                confidence=0.9,
                details={},
                timestamp="2024-01-01T00:00:00",
                address_hash="abc12345",
                rule_id="DR-ID-1"
            )
            for i in range(3)
        ]

        # Create mock database session
        mock_db = Mock()
        mock_db.commit = AsyncMock()
        mock_db.add = Mock()

        # Store events
        count = await detection_service.store_events(mock_events, mock_db)

        assert count == 3
        assert mock_db.add.call_count == 3
        mock_db.commit.assert_called_once()
