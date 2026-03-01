"""
Unit tests for risk assessment service
"""
import pytest
from datetime import datetime, timezone
from app.services.risk.assessment import (
    classify_risk_level,
    compute_risk_assessment,
    compute_comparative_assessment
)
from app.models import NetworkTraffic, RiskLevel


class TestClassifyRiskLevel:
    """Test classify_risk_level function"""

    def test_low_risk_score_0_to_30(self):
        """Test that scores 0-30 are classified as LOW"""
        assert classify_risk_level(0) == RiskLevel.LOW
        assert classify_risk_level(15) == RiskLevel.LOW
        assert classify_risk_level(30) == RiskLevel.LOW

    def test_medium_risk_score_31_to_50(self):
        """Test that scores 31-50 are classified as MEDIUM"""
        assert classify_risk_level(31) == RiskLevel.MEDIUM
        assert classify_risk_level(40) == RiskLevel.MEDIUM
        assert classify_risk_level(50) == RiskLevel.MEDIUM

    def test_high_risk_score_51_to_70(self):
        """Test that scores 51-70 are classified as HIGH"""
        assert classify_risk_level(51) == RiskLevel.HIGH
        assert classify_risk_level(60) == RiskLevel.HIGH
        assert classify_risk_level(70) == RiskLevel.HIGH

    def test_critical_risk_score_71_to_100(self):
        """Test that scores 71-100 are classified as CRITICAL"""
        assert classify_risk_level(71) == RiskLevel.CRITICAL
        assert classify_risk_level(85) == RiskLevel.CRITICAL
        assert classify_risk_level(100) == RiskLevel.CRITICAL


class TestComputeRiskAssessment:
    """Test compute_risk_assessment function"""

    @pytest.mark.asyncio
    async def test_empty_traffic_records(self):
        """Test assessment with empty traffic records"""
        session_id = "test-session-123"
        traffic_records = []

        assessment = await compute_risk_assessment(session_id, traffic_records)

        assert assessment.session_id == session_id
        assert 0 <= assessment.overall_score <= 100
        assert 0.0 <= assessment.entropy_score <= 1.0
        assert 0.0 <= assessment.uniqueness_score <= 1.0
        assert 0.0 <= assessment.correlation_score <= 1.0
        assert 0.0 <= assessment.temporal_score <= 1.0
        assert 0.0 <= assessment.confidence <= 1.0
        assert assessment.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert len(assessment.recommendations) >= 3
        assert len(assessment.recommendations) <= 5

    @pytest.mark.asyncio
    async def test_single_method_traffic(self):
        """Test assessment with single RPC method (low entropy)"""
        session_id = "test-session-456"
        timestamp = datetime.now(timezone.utc)

        traffic_records = [
            NetworkTraffic(
                id="1", session_id=session_id, method="POST", endpoint="/rpc",
                rpc_method="eth_getBalance", request_timestamp=timestamp,
                response_time_ms=100, response_status=200, response_size_bytes=500
            )
        ]

        assessment = await compute_risk_assessment(session_id, traffic_records)

        # Single method should have entropy_score = 0 (minimum diversity)
        assert assessment.entropy_score == 0.0
        assert assessment.session_id == session_id

    @pytest.mark.asyncio
    async def test_diverse_method_traffic(self):
        """Test assessment with diverse RPC methods (high entropy)"""
        session_id = "test-session-789"
        timestamp = datetime.now(timezone.utc)
        methods = ["eth_getBalance", "eth_blockNumber", "eth_getTransactionCount",
                   "eth_call", "eth_getBlockByNumber", "eth_estimateGas"]

        traffic_records = [
            NetworkTraffic(
                id=str(i), session_id=session_id, method="POST", endpoint="/rpc",
                rpc_method=methods[i], request_timestamp=timestamp,
                response_time_ms=100, response_status=200, response_size_bytes=500
            )
            for i, _ in enumerate(methods)
        ]

        assessment = await compute_risk_assessment(session_id, traffic_records)

        # Diverse methods should have higher entropy
        assert assessment.entropy_score > 0.5
        assert assessment.session_id == session_id

    @pytest.mark.asyncio
    async def test_single_address_correlation(self):
        """Test that single address session has 0 correlation"""
        session_id = "test-session-single-addr"
        timestamp = datetime.now(timezone.utc)

        traffic_records = [
            NetworkTraffic(
                id="1", session_id=session_id, method="POST", endpoint="/rpc",
                rpc_method="eth_getBalance", request_timestamp=timestamp,
                response_time_ms=100, response_status=200, response_size_bytes=500
            )
        ]

        assessment = await compute_risk_assessment(session_id, traffic_records)

        # Single address session should have correlation score of 0
        assert assessment.correlation_score == 0.0

    @pytest.mark.asyncio
    async def test_irregular_timing_high_temporal(self):
        """Test that irregular timing results in high temporal score"""
        session_id = "test-session-temporal"
        timestamps = [
            datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 10, 0, 1, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 10, 0, 2, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 10, 0, 15, tzinfo=timezone.utc),  # Large gap
            datetime(2026, 1, 1, 10, 0, 16, tzinfo=timezone.utc),
        ]

        traffic_records = [
            NetworkTraffic(
                id=str(i), session_id=session_id, method="POST", endpoint="/rpc",
                rpc_method="eth_getBalance", request_timestamp=timestamps[i],
                response_time_ms=100, response_status=200, response_size_bytes=500
            )
            for i in range(len(timestamps))
        ]

        assessment = await compute_risk_assessment(session_id, traffic_records)

        # Irregular timing should result in high temporal score
        assert assessment.temporal_score > 0.5

    @pytest.mark.asyncio
    async def test_overall_score_range(self):
        """Test that overall_score is within 0-100 range"""
        session_id = "test-session-range"
        timestamp = datetime.now(timezone.utc)

        traffic_records = [
            NetworkTraffic(
                id=str(i), session_id=session_id, method="POST", endpoint="/rpc",
                rpc_method=f"eth_method{i}", request_timestamp=timestamp,
                response_time_ms=100, response_status=200, response_size_bytes=500
            )
            for i in range(10)
        ]

        assessment = await compute_risk_assessment(session_id, traffic_records)

        assert 0 <= assessment.overall_score <= 100

    @pytest.mark.asyncio
    async def test_baseline_comparison_structure(self):
        """Test that baseline_comparison dict has correct structure"""
        session_id = "test-session-baseline"

        traffic_records = [
            NetworkTraffic(
                id="1", session_id=session_id, method="POST", endpoint="/rpc",
                rpc_method="eth_getBalance", request_timestamp=datetime.now(timezone.utc),
                response_time_ms=100, response_status=200, response_size_bytes=500
            )
        ]

        assessment = await compute_risk_assessment(session_id, traffic_records)

        assert assessment.baseline_comparison is not None
        assert "overall_score" in assessment.baseline_comparison
        assert "risk_level" in assessment.baseline_comparison
        assert "ideal_score" in assessment.baseline_comparison
        assert "worst_score" in assessment.baseline_comparison
        assert assessment.baseline_comparison["ideal_score"] == 0
        assert assessment.baseline_comparison["worst_score"] == 100

    @pytest.mark.asyncio
    async def test_confidence_interval_structure(self):
        """Test that confidence interval is properly structured"""
        session_id = "test-session-ci"

        traffic_records = [
            NetworkTraffic(
                id="1", session_id=session_id, method="POST", endpoint="/rpc",
                rpc_method="eth_getBalance", request_timestamp=datetime.now(timezone.utc),
                response_time_ms=100, response_status=200, response_size_bytes=500
            )
        ]

        assessment = await compute_risk_assessment(session_id, traffic_records)

        assert 0.0 <= assessment.confidence <= 1.0
        assert 0.0 <= assessment.confidence_interval_low <= assessment.confidence
        assert assessment.confidence <= assessment.confidence_interval_high <= 1.0

    @pytest.mark.asyncio
    async def test_assessment_structure(self):
        """Test that assessment has all required fields"""
        session_id = "test-session-structure"

        traffic_records = [
            NetworkTraffic(
                id="1", session_id=session_id, method="POST", endpoint="/rpc",
                rpc_method="eth_getBalance", request_timestamp=datetime.now(timezone.utc),
                response_time_ms=100, response_status=200, response_size_bytes=500
            )
        ]

        assessment = await compute_risk_assessment(session_id, traffic_records)

        # Verify ID and session_id
        assert assessment.id is not None
        assert len(assessment.id) == 36  # UUID format
        assert assessment.session_id == session_id

        # Verify all scores are present
        assert isinstance(assessment.overall_score, int)
        assert isinstance(assessment.entropy_score, float)
        assert isinstance(assessment.uniqueness_score, float)
        assert isinstance(assessment.correlation_score, float)
        assert isinstance(assessment.temporal_score, float)

        # Verify recommended structure
        assert isinstance(assessment.recommendations, list)
        assert len(assessment.recommendations) > 0


class TestComputeComparativeAssessment:
    """Test compute_comparative_assessment function"""

    @pytest.mark.asyncio
    async def test_single_session_comparative(self):
        """Test comparative assessment with single session"""
        session_ids = ["session-1"]
        traffic_records_by_session = {
            "session-1": [
                NetworkTraffic(
                    id="1", session_id="session-1", method="POST", endpoint="/rpc",
                    rpc_method="eth_getBalance", request_timestamp=datetime.now(timezone.utc),
                    response_time_ms=100, response_status=200, response_size_bytes=500
                )
            ]
        }

        assessments = await compute_comparative_assessment(session_ids, traffic_records_by_session)

        assert len(assessments) == 1
        assert "session-1" in assessments
        assert assessments["session-1"].session_id == "session-1"

    @pytest.mark.asyncio
    async def test_multiple_sessions_comparative(self):
        """Test comparative assessment with multiple sessions"""
        session_ids = ["session-1", "session-2", "session-3"]
        traffic_records_by_session = {
            sid: [
                NetworkTraffic(
                    id="1", session_id=sid, method="POST", endpoint="/rpc",
                    rpc_method="eth_getBalance", request_timestamp=datetime.now(timezone.utc),
                    response_time_ms=100, response_status=200, response_size_bytes=500
                )
            ]
            for sid in session_ids
        }

        assessments = await compute_comparative_assessment(session_ids, traffic_records_by_session)

        assert len(assessments) == 3
        for sid in session_ids:
            assert sid in assessments

    @pytest.mark.asyncio
    async def test_comparative_baseline_stats(self):
        """Test that comparative assessment includes baseline stats"""
        session_ids = ["session-1", "session-2"]
        traffic_records_by_session = {
            sid: [
                NetworkTraffic(
                    id="1", session_id=sid, method="POST", endpoint="/rpc",
                    rpc_method="eth_getBalance", request_timestamp=datetime.now(timezone.utc),
                    response_time_ms=100 + i * 10, response_status=200, response_size_bytes=500
                )
            ]
            for i, sid in enumerate(session_ids)
        }

        assessments = await compute_comparative_assessment(session_ids, traffic_records_by_session)

        # Check that baseline_comparison includes peer stats
        for assessment in assessments.values():
            baseline = assessment.baseline_comparison
            assert "peer_average" in baseline
            assert "peer_range" in baseline
            assert "percentile" in baseline

    @pytest.mark.asyncio
    async def test_empty_session_list_comparative(self):
        """Test comparative assessment with empty session list"""
        session_ids = []
        traffic_records_by_session = {}

        assessments = await compute_comparative_assessment(session_ids, traffic_records_by_session)

        assert len(assessments) == 0
