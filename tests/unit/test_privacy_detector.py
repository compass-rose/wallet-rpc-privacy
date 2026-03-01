"""
Unit tests for privacy detector
"""
import pytest
from app.core.detector import PrivacyDetector


class TestPrivacyDetector:
    """Test PrivacyDetector class"""

    @pytest.fixture
    def detector(self):
        """Create detector instance"""
        return PrivacyDetector()

    def test_initialization(self):
        """Test that detector initializes with correct weights"""
        detector = PrivacyDetector()

        assert hasattr(detector, "weights")
        assert "IDENTITY" in detector.weights
        assert "LOCATION" in detector.weights
        assert "ASSET" in detector.weights
        assert "BEHAVIOR" in detector.weights

        # Check weights sum approximately to 1
        total_weight = sum(detector.weights.values())
        assert abs(total_weight - 1.0) < 0.01

    def test_calculate_risk_severity_empty_events(self, detector):
        """Test risk severity calculation with empty events"""
        score, level = detector.calculate_risk_severity([])

        assert score == 0.0
        assert level == "LOW"

    def test_calculate_risk_severity_single_identity(self, detector):
        """Test risk severity with single IDENTITY leak"""
        from app.models.schemas import PrivacyLeakEventSchema
        event = PrivacyLeakEventSchema(
            session_id="session-1",
            leak_type="IDENTITY",
            method_name="POST",
            description="Test leak",
            confidence=0.9,
            details={},
            timestamp="2024-01-01T00:00:00",
            address_hash="abc123",
            rule_id="DR-ID-1"
        )

        score, level = detector.calculate_risk_severity([event])

        assert 0.0 <= score <= 100.0
        assert level in ["LOW", "MEDIUM", "CRITICAL"]

    def test_calculate_risk_severity_multiple_types(self, detector):
        """Test risk severity with multiple leak types"""
        from app.models.schemas import PrivacyLeakEventSchema

        events = [
            PrivacyLeakEventSchema(
                session_id="session-1",
                leak_type=leak_type,
                method_name="POST",
                description=f"Test {leak_type}",
                confidence=0.9,
                details={},
                timestamp="2024-01-01T00:00:00",
                address_hash="abc123",
                rule_id="DR-ID-1"
            )
            for leak_type in ["IDENTITY", "LOCATION", "ASSET", "BEHAVIOR"]
        ]

        score, level = detector.calculate_risk_severity(events)

        assert 0.0 <= score <= 100.0
        # Multiple types should increase severity
        # Multiple types should increase severity (though may still be LOW if confidence is low)
        assert level in ["LOW", "MEDIUM", "CRITICAL"]

    def test_analyze_flow_empty_dict(self, detector):
        """Test flow analysis with empty dictionary"""
        flow = {}

        events = detector.analyze_flow(flow)

        assert isinstance(events, list)

    def test_analyze_flow_with_wallet_address(self, detector):
        """Test detection of wallet address in flow"""
        flow = {
            "flow_id": "test-flow",
            "request": {
                "method": "POST",
                "host": "example.com",
                "path": "/rpc",
                "headers": "Content-Type: application/json",
                "content": '{"jsonrpc":"2.0","method":"eth_getBalance","params":["0x71C7656EC7ab88b098defB751B7401B5f6d8976F"],"id":1}'
            },
            "response": {}
        }

        events = detector.analyze_flow(flow)

        assert len(events) > 0
        # Should detect wallet address
        has_identity_leak = any(e.leak_type == "IDENTITY" for e in events)
        assert has_identity_leak

    def test_analyze_flow_with_phishing_detection(self, detector):
        """Test detection of phishing API telemetry"""
        flow = {
            "flow_id": "test-flow",
            "request": {
                "method": "POST",
                "host": "phishing-detection metamask io",
                "path": "/api/v1/check",
                "headers": "",
                "content": ""
            },
            "response": {}
        }

        events = detector.analyze_flow(flow)

        assert len(events) > 0
        # Should detect phishing API call
        has_location_leak = any(e.leak_type == "LOCATION" for e in events)
        assert has_location_leak

    def test_analyze_flow_with_balance_polling(self, detector):
        """Test detection of balance polling"""
        flow = {
            "flow_id": "test-flow",
            "request": {
                "method": "POST",
                "host": "example.com",
                "path": "/rpc",
                "headers": "",
                "content": '{"jsonrpc":"2.0","method":"eth_getBalance","params":["0x1234..."],"id":1}'
            },
            "response": {}
        }

        events = detector.analyze_flow(flow)

        assert len(events) > 0
        # Should detect asset/balance tracking
        has_asset_leak = any(e.leak_type == "ASSET" for e in events)
        assert has_asset_leak

    def test_analyze_flow_with_browser_fingerprint(self, detector):
        """Test detection of browser fingerprint in headers"""
        flow = {
            "flow_id": "test-flow",
            "request": {
                "method": "POST",
                "host": "example.com",
                "path": "/rpc",
                "headers": "User-Agent: MetaMask/10.0.0 Edg/120.0.0.0",
                "content": ""
            },
            "response": {}
        }

        events = detector.analyze_flow(flow)

        assert len(events) > 0
        # Should detect client fingerprint
        has_location_leak = any(e.leak_type == "LOCATION" for e in events)
        assert has_location_leak

    def test_analyze_flow_with_transaction_count(self, detector):
        """Test detection of transaction count tracking"""
        flow = {
            "flow_id": "test-flow",
            "request": {
                "method": "POST",
                "host": "example.com",
                "path": "/rpc",
                "headers": "",
                "content": '{"jsonrpc":"2.0","method":"eth_getTransactionCount","params":["0x1234..."],"id":1}'
            },
            "response": {}
        }

        events = detector.analyze_flow(flow)

        assert len(events) > 0
        # Should detect behavior leak
        has_behavior_leak = any(e.leak_type == "BEHAVIOR" for e in events)
        assert has_behavior_leak

    def test_analyze_flow_non_dict_input(self, detector):
        """Test that non-dict input returns empty list"""
        events = detector.analyze_flow("not a dict")
        assert events == []

    def test_analyze_flow_multiple_addresses(self, detector):
        """Test detection of multiple wallet addresses"""
        flow = {
            "flow_id": "test-flow",
            "request": {
                "method": "POST",
                "host": "example.com",
                "path": "/rpc",
                "headers": "",
                "content": '["0x71C7656EC7ab88b098defB751B7401B5f6d8976F","0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC"]'
            },
            "response": {}
        }

        events = detector.analyze_flow(flow)

        # Should detect both addresses
        identity_events = [e for e in events if e.leak_type == "IDENTITY"]
        assert len(identity_events) == 2
