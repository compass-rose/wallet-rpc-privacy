"""
Unit tests for risk service wrapper
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.risk_service import RiskService
from app.models import RiskAssessment, NetworkTraffic, RiskLevel
from app.services.risk_service import RiskService
from app.models import RiskAssessment, NetworkTraffic, RiskLevel


class TestRiskService:
    """Test RiskService class"""

    @pytest.fixture
    def risk_service(self):
        """Create risk service instance"""
        return RiskService()

    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        db = Mock(spec=AsyncSession)
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        db.add = Mock()
        return db

    @pytest.fixture
    def sample_traffic(self):
        """Create sample traffic records"""
        timestamp = datetime.now(timezone.utc)
        return [
            NetworkTraffic(
                id="1",
                session_id="test-session-1",
                method="POST",
                endpoint="/rpc",
                rpc_method="eth_getBalance",
                request_timestamp=timestamp,
                response_time_ms=100,
                response_status=200,
                response_size_bytes=500
            )
        ]

    @pytest.mark.asyncio
    async def test_assess_session_delegates_to_core(self, risk_service, sample_traffic):
        """Test that assess_session delegates to compute_risk_assessment"""
        session_id = "test-session-1"

        with patch('app.services.risk_service.compute_risk_assessment') as mock_compute:
            mock_assessment = RiskAssessment(
                id="1",
                session_id=session_id,
                overall_score=50,
                entropy_score=0.5,
                uniqueness_score=0.5,
                correlation_score=0.5,
                temporal_score=0.5,
                confidence=0.9,
                risk_level=RiskLevel.MEDIUM,
                recommendations=["Test recommendation"],
                created_at=datetime.now(timezone.utc)
            )
            mock_compute.return_value = mock_assessment

            result = await risk_service.assess_session(session_id, sample_traffic)

            assert result.session_id == session_id
            mock_compute.assert_called_once_with(session_id, sample_traffic)

    @pytest.mark.asyncio
    async def test_assess_session_with_empty_traffic(self, risk_service):
        """Test that assess_session handles empty traffic list"""
        session_id = "test-session-empty"
        empty_traffic = []

        with patch('app.services.risk_service.compute_risk_assessment') as mock_compute:
            mock_assessment = RiskAssessment(
                id="1",
                session_id=session_id,
                overall_score=0,
                entropy_score=0.0,
                uniqueness_score=0.0,
                correlation_score=0.0,
                temporal_score=0.0,
                confidence=1.0,
                risk_level=RiskLevel.LOW,
                recommendations=[],
                created_at=datetime.now(timezone.utc)
            )
            mock_compute.return_value = mock_assessment

            result = await risk_service.assess_session(session_id, empty_traffic)

            assert result.session_id == session_id
            mock_compute.assert_called_once()

    @pytest.mark.asyncio
    async def test_store_assessment_with_mock_db(self, risk_service, mock_db):
        """Test storing assessment in database"""
        assessment = RiskAssessment(
            id="1",
            session_id="test-session-1",
            overall_score=75,
            entropy_score=0.7,
            uniqueness_score=0.6,
            correlation_score=0.8,
            temporal_score=0.9,
            confidence=0.85,
            risk_level=RiskLevel.HIGH,
            recommendations=["Recommendation 1", "Recommendation 2"],
            created_at=datetime.now(timezone.utc)
        )

        result = await risk_service.store_assessment(assessment, mock_db)

        mock_db.add.assert_called_once_with(assessment)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(assessment)
        assert result == assessment

    @pytest.mark.asyncio
    async def test_store_multiple_assessments(self, risk_service, mock_db):
        """Test storing multiple assessments sequentially"""
        for i in range(3):
            assessment = RiskAssessment(
                id=str(i),
                session_id=f"test-session-{i}",
                overall_score=i * 10,
                entropy_score=0.1 * i,
                uniqueness_score=0.1 * i,
                correlation_score=0.1 * i,
                temporal_score=0.1 * i,
                confidence=0.9,
                risk_level=RiskLevel.LOW,
                recommendations=[],
                created_at=datetime.now(timezone.utc)
            )

            await risk_service.store_assessment(assessment, mock_db)

            assert mock_db.add.call_count == i + 1
            assert mock_db.commit.call_count == i + 1

    @pytest.mark.asyncio
    async def test_get_latest_assessment_found(self, risk_service):
        """Test getting latest assessment when it exists"""
        session_id = "test-session-1"
        mock_assessment = RiskAssessment(
            id="1",
            session_id=session_id,
            overall_score=60,
            entropy_score=0.6,
            uniqueness_score=0.6,
            correlation_score=0.6,
            temporal_score=0.6,
            confidence=0.9,
            risk_level=RiskLevel.HIGH,
            recommendations=[],
            created_at=datetime.now(timezone.utc)
        )

        mock_db = Mock(spec=AsyncSession)
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_assessment
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await risk_service.get_latest_assessment(session_id, mock_db)

        assert result is not None
        assert result.session_id == session_id
        assert result.overall_score == 60
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_latest_assessment_not_found(self, risk_service):
        """Test getting latest assessment when it doesn't exist"""
        session_id = "non-existent-session"

        mock_db = Mock(spec=AsyncSession)
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await risk_service.get_latest_assessment(session_id, mock_db)

        assert result is None
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_assessments_default_pagination(self, risk_service):
        """Test getting all assessments with default pagination"""
        mock_db = Mock(spec=AsyncSession)
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [
            RiskAssessment(
                id=str(i),
                session_id=f"session-{i}",
                overall_score=i * 10,
                entropy_score=0.1,
                uniqueness_score=0.1,
                correlation_score=0.1,
                temporal_score=0.1,
                confidence=0.9,
                risk_level=RiskLevel.LOW,
                recommendations=[],
                created_at=datetime.now(timezone.utc)
            )
            for i in range(5)
        ]
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await risk_service.get_all_assessments(mock_db)

        assert len(result) == 5
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_assessments_custom_pagination(self, risk_service):
        """Test getting all assessments with custom pagination"""
        skip = 10
        limit = 20

        mock_db = Mock(spec=AsyncSession)
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [
            RiskAssessment(
                id="1",
                session_id="session-1",
                overall_score=50,
                entropy_score=0.5,
                uniqueness_score=0.5,
                correlation_score=0.5,
                temporal_score=0.5,
                confidence=0.9,
                risk_level=RiskLevel.MEDIUM,
                recommendations=[],
                created_at=datetime.now(timezone.utc)
            )
        ]
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await risk_service.get_all_assessments(mock_db, skip=skip, limit=limit)

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_all_assessments_empty(self, risk_service):
        """Test getting all assessments when none exist"""
        mock_db = Mock(spec=AsyncSession)
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await risk_service.get_all_assessments(mock_db)

        assert len(result) == 0
        assert result == []

    @pytest.mark.asyncio
    async def test_service_initialization(self):
        """Test that RiskService can be instantiated"""
        service = RiskService()
        assert isinstance(service, RiskService)
        assert hasattr(service, 'assess_session')
        assert hasattr(service, 'store_assessment')
        assert hasattr(service, 'get_latest_assessment')
        assert hasattr(service, 'get_all_assessments')
