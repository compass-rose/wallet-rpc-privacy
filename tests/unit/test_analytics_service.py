"""
Unit tests for analytics service
"""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.analytics import AnalyticsService
from app.models import Session, NetworkTraffic, PrivacyLeakEvent, RiskAssessment, RiskLevel, SessionStatus


class TestAnalyticsService:
    """Test AnalyticsService class"""

    @pytest.fixture
    def analytics_service(self):
        """Create analytics service instance"""
        return AnalyticsService()

    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        db = Mock(spec=AsyncSession)
        db.execute = AsyncMock()
        return db

    @pytest.mark.asyncio
    async def test_get_summary_stats_with_data(self, analytics_service, mock_db):
        """Test getting summary statistics when database has data"""
        # Create mock result for session count
        mock_result = Mock()
        
        # Setup scalar_one to return counts
        call_count = [0]
        def scalar_side_effect():
            call_count[0] += 1
            if call_count[0] == 5:  # Average query
                return 65.5
            return 10  # Count queries
        
        mock_result.scalar_one.side_effect = scalar_side_effect
        
        # Mock status counts
        status = Mock()
        status.value = "active"
        mock_status_row = [status, 10]
        mock_result.all.return_value = [mock_status_row]
        
        mock_db.execute.return_value = mock_result

        result = await analytics_service.get_summary_stats(mock_db)

        assert result["total_sessions"] == 10
        assert mock_db.execute.call_count == 6  # 6 queries total
        assert "total_traffic" in result
        assert "total_leaks" in result
        assert "total_assessments" in result
        assert result["average_risk_score"] == 65.5
        assert "sessions_by_status" in result

    @pytest.mark.asyncio
    async def test_get_summary_stats_empty_database(self, analytics_service, mock_db):
        """Test getting summary statistics when database is empty"""
        # Mock scalar_one to return None for all counts
        scalar_call_count = [0]

        def scalar_side_effect():
            scalar_call_count[0] += 1
            if scalar_call_count[0] <= 4:  # First 4 are count queries
                return None
            else:  # 5th is avg query
                return None

        mock_result = Mock()
        mock_result.scalar_one.side_effect = scalar_side_effect
        # Mock the group_by query result to return empty list
        mock_result.all.return_value = []
        mock_db.execute.return_value = mock_result

        result = await analytics_service.get_summary_stats(mock_db)

        assert result["total_sessions"] == 0
        assert result["total_traffic"] == 0
        assert result["total_leaks"] == 0
        assert result["total_assessments"] == 0
        assert result["average_risk_score"] == 0
        assert result["sessions_by_status"] == {}

    @pytest.mark.asyncio
    async def test_get_trends_default_days(self, analytics_service, mock_db):
        """Test getting trends with default 7 days"""
        # Create mock row for trends
        mock_row = Mock()
        mock_row.date = datetime.now(timezone.utc).date()
        mock_row.count = 5
        mock_row.avg_score = 45.5

        mock_result = Mock()
        mock_result.all.return_value = [mock_row]
        mock_db.execute.return_value = mock_result

        result = await analytics_service.get_trends(mock_db)

        assert result["days"] == 7
        assert "session_trends" in result
        assert "risk_trends" in result
        assert len(result["session_trends"]) == 1
        assert len(result["risk_trends"]) == 1
        assert mock_db.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_get_trends_custom_days(self, analytics_service, mock_db):
        """Test getting trends with custom days"""
        days_count = 30

        mock_result = Mock()
        mock_result.all.return_value = []
        mock_db.execute.return_value = mock_result

        result = await analytics_service.get_trends(mock_db, days=days_count)

        assert result["days"] == days_count
        assert result["session_trends"] == []
        assert result["risk_trends"] == []

    @pytest.mark.asyncio
    async def test_get_trends_multiple_days(self, analytics_service, mock_db):
        """Test getting trends with multiple days of data"""
        # Create mock rows for 3 days
        mock_rows = []
        for i in range(3):
            row = Mock()
            row.date = (datetime.now(timezone.utc) - timedelta(days=i)).date()
            row.count = i + 1
            row.avg_score = 40.0 + i * 10
            mock_rows.append(row)

        mock_result = Mock()
        mock_result.all.return_value = mock_rows
        mock_db.execute.return_value = mock_result

        result = await analytics_service.get_trends(mock_db)

        assert len(result["session_trends"]) == 3
        assert len(result["risk_trends"]) == 3

    @pytest.mark.asyncio
    async def test_get_leak_distribution(self, analytics_service, mock_db):
        """Test getting privacy leak type distribution"""
        # Create mock leak type rows
        leak_type = Mock()
        leak_type.value = "identity"

        mock_row = Mock()
        mock_row.leak_type = leak_type
        mock_row.count = 25

        mock_result = Mock()
        mock_result.all.return_value = [mock_row]
        mock_db.execute.return_value = mock_result

        result = await analytics_service.get_leak_distribution(mock_db)

        assert len(result) == 1
        assert result["identity"] == 25
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_leak_distribution_multiple_types(self, analytics_service, mock_db):
        """Test getting distribution with multiple leak types"""
        # Create mock leak type rows with different types
        mock_rows = []
        leak_types = ["identity", "asset", "behavior", "location"]
        counts = [25, 15, 30, 10]

        for leak_type_str, count in zip(leak_types, counts):
            row = Mock()
            leak_type = Mock()
            leak_type.value = leak_type_str
            row.leak_type = leak_type
            row.count = count
            mock_rows.append(row)

        mock_result = Mock()
        mock_result.all.return_value = mock_rows
        mock_db.execute.return_value = mock_result

        result = await analytics_service.get_leak_distribution(mock_db)

        assert len(result) == 4
        assert result["identity"] == 25
        assert result["asset"] == 15
        assert result["behavior"] == 30
        assert result["location"] == 10

    @pytest.mark.asyncio
    async def test_get_risk_level_distribution(self, analytics_service, mock_db):
        """Test getting risk level distribution"""
        # Create mock risk level rows
        risk_level = Mock()
        risk_level.value = "medium"

        mock_row = Mock()
        mock_row.risk_level = risk_level
        mock_row.count = 15

        mock_result = Mock()
        mock_result.all.return_value = [mock_row]
        mock_db.execute.return_value = mock_result

        result = await analytics_service.get_risk_level_distribution(mock_db)

        assert len(result) == 1
        assert result["medium"] == 15

    @pytest.mark.asyncio
    async def test_get_risk_level_distribution_all_levels(self, analytics_service, mock_db):
        """Test getting distribution with all risk levels"""
        risk_levels = ["low", "medium", "high", "critical"]
        counts = [30, 25, 15, 5]

        mock_rows = []
        for level_str, count in zip(risk_levels, counts):
            row = Mock()
            risk_level = Mock()
            risk_level.value = level_str
            row.risk_level = risk_level
            row.count = count
            mock_rows.append(row)

        mock_result = Mock()
        mock_result.all.return_value = mock_rows
        mock_db.execute.return_value = mock_result

        result = await analytics_service.get_risk_level_distribution(mock_db)

        assert len(result) == 4
        assert result["low"] == 30
        assert result["medium"] == 25
        assert result["high"] == 15
        assert result["critical"] == 5

    @pytest.mark.asyncio
    async def test_get_method_frequencies_default_limit(self, analytics_service, mock_db):
        """Test getting method frequencies with default limit"""
        # Create mock method rows
        mock_rows = []
        methods = ["eth_getBalance", "eth_blockNumber", "eth_getTransactionCount"]
        for i, method in enumerate(methods):
            row = Mock()
            row.rpc_method = method
            row.count = (3 - i) * 10  # 30, 20, 10
            mock_rows.append(row)

        mock_result = Mock()
        mock_result.all.return_value = mock_rows
        mock_db.execute.return_value = mock_result

        result = await analytics_service.get_method_frequencies(mock_db)

        assert len(result) == 3
        assert result[0]["method"] == "eth_getBalance"
        assert result[0]["count"] == 30
        assert result[1]["method"] == "eth_blockNumber"
        assert result[1]["count"] == 20

    @pytest.mark.asyncio
    async def test_get_method_frequencies_custom_limit(self, analytics_service, mock_db):
        """Test getting method frequencies with custom limit"""
        limit = 5

        mock_result = Mock()
        mock_result.all.return_value = []
        mock_db.execute.return_value = mock_result

        result = await analytics_service.get_method_frequencies(mock_db, limit=limit)

        assert result == []
        # Verify that limit was passed in the query
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_method_frequencies_one_result(self, analytics_service, mock_db):
        """Test getting method frequencies with single method"""
        method_name = "eth_call"
        method_count = 100

        mock_row = Mock()
        mock_row.rpc_method = method_name
        mock_row.count = method_count

        mock_result = Mock()
        mock_result.all.return_value = [mock_row]
        mock_db.execute.return_value = mock_result

        result = await analytics_service.get_method_frequencies(mock_db, limit=1)

        assert len(result) == 1
        assert result[0]["method"] == method_name
        assert result[0]["count"] == method_count

    @pytest.mark.asyncio
    async def test_get_top_risk_sessions(self, analytics_service, mock_db):
        """Test getting sessions with highest risk scores"""
        # Create mock session rows with risk data
        mock_row = Mock()
        mock_row.session_id = "session-1"
        mock_row.wallet_type = "MetaMask"
        mock_row.rpc_provider = "https://mainnet.infura.io/v3/test"
        mock_row.overall_score = 85
        risk_level = Mock()
        risk_level.value = "critical"
        mock_row.risk_level = risk_level
        mock_row.assessed_at = datetime.now(timezone.utc)

        mock_result = Mock()
        mock_result.all.return_value = [mock_row]
        mock_db.execute.return_value = mock_result

        result = await analytics_service.get_top_risk_sessions(mock_db)

        assert len(result) == 1
        assert result[0]["session_id"] == "session-1"
        assert result[0]["wallet_type"] == "MetaMask"
        assert result[0]["overall_score"] == 85
        assert result[0]["risk_level"] == "critical"

    @pytest.mark.asyncio
    async def test_get_top_risk_sessions_custom_limit(self, analytics_service, mock_db):
        """Test getting top risk sessions with custom limit"""
        limit = 5

        mock_result = Mock()
        mock_result.all.return_value = []
        mock_db.execute.return_value = mock_result

        result = await analytics_service.get_top_risk_sessions(mock_db, limit=limit)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_top_risk_sessions_multiple(self, analytics_service, mock_db):
        """Test getting multiple top risk sessions"""
        mock_rows = []
        for i in range(3):
            row = Mock()
            row.session_id = f"session-{i}"
            row.wallet_type = "MetaMask"
            row.rpc_provider = "https://mainnet.infura.io/v3/test"
            row.overall_score = 90 - i * 10  # 90, 80, 70
            risk_level = Mock()
            risk_level.value = ["critical", "high", "medium"][i]
            row.risk_level = risk_level
            row.assessed_at = datetime.now(timezone.utc)
            mock_rows.append(row)

        mock_result = Mock()
        mock_result.all.return_value = mock_rows
        mock_db.execute.return_value = mock_result

        result = await analytics_service.get_top_risk_sessions(mock_db)

        assert len(result) == 3
        assert result[0]["overall_score"] == 90
        assert result[1]["overall_score"] == 80
        assert result[2]["overall_score"] == 70

    @pytest.mark.asyncio
    async def test_get_response_time_stats_with_data(self, analytics_service, mock_db):
        """Test getting response time statistics when data exists"""
        # Create mock result row
        mock_row = Mock()
        mock_row.avg = 150.5
        mock_row.min = 50
        mock_row.max = 500

        mock_result = Mock()
        mock_result.one_or_none.return_value = mock_row
        mock_db.execute.return_value = mock_result

        result = await analytics_service.get_response_time_stats(mock_db)

        assert result["average_ms"] == 150.5
        assert result["min_ms"] == 50
        assert result["max_ms"] == 500

    @pytest.mark.asyncio
    async def test_get_response_time_stats_no_data(self, analytics_service, mock_db):
        """Test getting response time statistics when no data exists"""
        mock_result = Mock()
        mock_result.one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await analytics_service.get_response_time_stats(mock_db)

        assert result["avg"] == 0
        assert result["min"] == 0
        assert result["max"] == 0

    @pytest.mark.asyncio
    async def test_get_response_time_stats_rounding(self, analytics_service, mock_db):
        """Test that response time statistics are properly rounded"""
        # Create mock result row with decimal values
        mock_row = Mock()
        mock_row.avg = 150.555555
        mock_row.min = 50.1
        mock_row.max = 500.9

        mock_result = Mock()
        mock_result.one_or_none.return_value = mock_row
        mock_db.execute.return_value = mock_result

        result = await analytics_service.get_response_time_stats(mock_db)

        assert result["average_ms"] == 150.56  # rounded to 2 decimal places
        assert result["min_ms"] == 50.1
        assert result["max_ms"] == 500.9

    @pytest.mark.asyncio
    async def test_service_initialization(self):
        """Test that AnalyticsService can be instantiated"""
        service = AnalyticsService()
        assert isinstance(service, AnalyticsService)
        assert hasattr(service, 'get_summary_stats')
        assert hasattr(service, 'get_trends')
        assert hasattr(service, 'get_leak_distribution')
        assert hasattr(service, 'get_risk_level_distribution')
        assert hasattr(service, 'get_method_frequencies')
        assert hasattr(service, 'get_top_risk_sessions')
        assert hasattr(service, 'get_response_time_stats')

    @pytest.mark.asyncio
    async def test_get_summary_stats_rounding(self, analytics_service, mock_db):
        """Test that average risk score is rounded properly"""
        # Setup for average query (6th call)
        call_count = [0]

        def scalar_side_effect():
            call_count[0] += 1
            if call_count[0] == 5:  # Average score query
                return 65.5555  # Should round to 65.56
            return 10  # Default count

        mock_result = Mock()
        mock_result.scalar_one.side_effect = scalar_side_effect
        mock_result.all.return_value = []
        mock_db.execute.return_value = mock_result

        result = await analytics_service.get_summary_stats(mock_db)

        assert result["average_risk_score"] == 65.56

    @pytest.mark.asyncio
    async def test_get_trends_risk_score_rounding(self, analytics_service, mock_db):
        """Test that risk trends are rounded properly"""
        # Create mock row with decimal average score
        mock_row = Mock()
        mock_row.date = datetime.now(timezone.utc).date()
        mock_row.count = 5
        mock_row.avg_score = 45.5555  # Should round to 45.56

        mock_result = Mock()
        mock_result.all.return_value = [mock_row]
        mock_db.execute.return_value = mock_result

        result = await analytics_service.get_trends(mock_db)

        assert len(result["risk_trends"]) == 1
        assert result["risk_trends"][0]["average_risk_score"] == 45.56
