"""
Unit tests for detection engine
"""
import pytest
from app.services.detection.engine import RuleEngine
from app.models import NetworkTraffic
from datetime import datetime, timezone


@pytest.fixture
def sample_traffic():
    """Create sample traffic records"""
    return [
        NetworkTraffic(
            id="traffic-1",
            session_id="session-1",
            method="POST",
            endpoint="https://example.com",
            rpc_method="eth_getBalance",
            request_timestamp=datetime.now(timezone.utc),
            response_time_ms=100,
            response_status=200
        ),
        NetworkTraffic(
            id="traffic-2",
            session_id="session-1",
            method="POST",
            endpoint="https://example.com",
            rpc_method="eth_getBalance",
            request_timestamp=datetime.now(timezone.utc),
            response_time_ms=150,
            response_status=200
        ),
        NetworkTraffic(
            id="traffic-3",
            session_id="session-1",
            method="POST",
            endpoint="https://example.com",
            rpc_method="eth_call",
            request_timestamp=datetime.now(timezone.utc),
            response_time_ms=200,
            response_status=200
        )
    ]


@pytest.mark.asyncio
async def test_rule_engine_loads_rules():
    """Test that rule engine loads YAML rules"""
    engine = RuleEngine()

    rules = engine.get_all_rules()

    assert len(rules) >= 10  # Should have at least 10 rules


@pytest.mark.asyncio
async def test_rule_engine_get_rules_summary():
    """Test rule summary"""
    engine = RuleEngine()

    summary = engine.get_rules_summary()

    assert summary["total"] >= 10
    assert "by_category" in summary
    assert summary["enabled"] <= summary["total"]


@pytest.mark.asyncio
async def test_rule_engine_evaluate_single_rule(sample_traffic):
    """Test evaluation against a single rule"""

    # This test verifies the evaluation logic runs without errors
    # In a real scenario, specific rule behavior would be tested
    engine = RuleEngine()

    # Get first rule
    rules = engine.loader.get_enabled_rules()
    if rules:
        rule = rules[0]

        # This should not raise an error
        matches = await engine._matches_conditions(rule, sample_traffic)

        # Result should be a boolean
        assert isinstance(matches, bool)


@pytest.mark.asyncio
async def test_rule_loader():
    """Test rule loader"""
    from app.services.detection.loader import RuleLoader

    loader = RuleLoader()
    rules = loader.load_rules()

    assert len(rules) >= 10

    # Test getting specific rule
    some_rule = next(iter(rules.values()))
    assert some_rule.rule_id is not None
    assert some_rule.name is not None
