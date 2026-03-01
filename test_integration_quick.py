#!/usr/bin/env python3
"""
Quick integration test for the backend system
"""
import asyncio
from app.services.traffic.mock_provider import MockTrafficProvider
from app.services.traffic.base import CaptureConfig
from app.services.risk.assessment import compute_risk_assessment
from app.services.detection.engine import RuleEngine


async def test_full_flow():
    """Test the complete flow from traffic capture to risk assessment"""
    print("=== Backend System Integration Test ===\n")

    # Test 1: Mock Traffic Provider
    print("1. Testing Mock Traffic Provider...")
    provider = MockTrafficProvider(count=50)
    config = CaptureConfig(
        wallet_type="MetaMask",
        rpc_provider="https://mainnet.infura.io/v3/test",
        packet_count=50
    )
    status = await provider.start_capture("test-session", config)
    print(f"   ✓ Capture started: active={status.active}")

    # Test 2: Generate Traffic Records
    print("\n2. Generating Traffic Records...")
    traffic_records = []
    async for record in provider.get_traffic_stream("test-session"):
        from app.services.traffic.base import TrafficRecord
        # Recreate record to simulate database storage
        traffic_records.append(record)
    print(f"   ✓ Generated {len(traffic_records)} traffic records")

    # Test 3: Risk Assessment
    print("\n3. Testing Risk Assessment...")
    try:
        # Need to create mock NetworkTraffic objects
        from app.models.traffic import NetworkTraffic
        from datetime import datetime, timezone

        mock_traffic = []
        for i, record in enumerate(traffic_records):
            mock_traffic.append(
                NetworkTraffic(
                    id=f"traffic-{i}",
                    session_id="test-session",
                    method="POST",
                    endpoint=config.rpc_provider,
                    rpc_method=record.rpc_method,
                    request_timestamp=record.request_timestamp,
                    response_time_ms=record.response_time_ms,
                    response_status=record.response_status,
                    user_agent=record.user_agent
                )
            )

        assessment = await compute_risk_assessment("test-session", mock_traffic)
        print(f"   ✓ Risk assessment completed")
        print(f"   ✓ Overall score: {assessment.overall_score}")
        print(f"   ✓ Risk level: {assessment.risk_level.value}")
        print(f"   ✓ Recommendations: {len(assessment.recommendations)} suggestions")

    except Exception as e:
        print(f"   ✗ Risk assessment failed: {e}")

    # Test 4: Detection Engine
    print("\n4. Testing Detection Rule Engine...")
    try:
        engine = RuleEngine()
        rules_summary = engine.get_rules_summary()
        print(f"   ✓ Detection engine loaded")
        print(f"   ✓ Total rules: {rules_summary['total']}")
        print(f"   ✓ Enabled rules: {rules_summary['enabled']}")

        # Test rule evaluation
        leak_events = await engine.evaluate_session("test-session", mock_traffic[:10])
        print(f"   ✓ Detected {len(leak_events)} leak events")

    except Exception as e:
        print(f"   ✗ Detection engine failed: {e}")

    print("\n=== All Tests Completed ===")


if __name__ == "__main__":
    asyncio.run(test_full_flow())
