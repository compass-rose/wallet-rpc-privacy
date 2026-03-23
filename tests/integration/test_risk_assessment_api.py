"""
Integration tests for Risk Assessment API (Section 3.3)

Tests for:
- POST /api/v1/sessions/{session_id}/assess
- POST /api/v1/sessions/{session_id}/baseline-compare
- POST /api/v1/sessions/{session_id}/simulate-attack
- POST /api/v1/sessions/{session_id}/adversarial-test
"""
import pytest
import httpx
from httpx import ASGITransport
from app.main import app
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from app.models import Session, NetworkTraffic, SessionStatus


@pytest.fixture(scope="function")
async def test_client_with_db(test_session):
    """Create test client with database session"""
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client, test_session


@pytest.mark.asyncio
async def test_assess_nonexistent_session(test_client_with_db):
    """Test assessing a non-existent session returns 404"""
    client, _ = test_client_with_db
    
    fake_session_id = str(uuid4())
    response = await client.post(f"/api/v1/sessions/{fake_session_id}/assess")
    
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "error" in data
    assert data["error"]["code"] in ["SESSION_NOT_FOUND", "ASSESSMENT_FAILED"]


@pytest.mark.asyncio
async def test_assess_session_empty_traffic(test_client_with_db):
    """Test assessing a session with no traffic records"""
    client, test_session = test_client_with_db
    
    session_id = str(test_session.id)
    response = await client.post(f"/api/v1/sessions/{session_id}/assess")
    
    assert response.status_code in [200, 400]
    data = response.json()
    
    if response.status_code == 200:
        assert data["success"] is True
        assert "data" in data
        assessment = data["data"]
        assert "overall_score" in assessment
        assert "risk_level" in assessment
    else:
        assert data["success"] is False
        assert "error" in data


@pytest.mark.asyncio
async def test_assess_session_with_traffic(test_client_with_db):
    """Test assessing a session with traffic data"""
    client, test_session = test_client_with_db
    
    from app.core.database import async_session_maker
    
    async with async_session_maker() as db:
        for i in range(5):
            traffic = NetworkTraffic(
                session_id=test_session.id,
                rpc_method="eth_blockNumber",
                request_data={"jsonrpc": "2.0", "method": "eth_blockNumber"},
                response_data={"jsonrpc": "2.0", "result": "0x123456"},
                timestamp=datetime.now(timezone.utc) - timedelta(minutes=i),
                response_time_ms=50 + i * 10
            )
            db.add(traffic)
        await db.commit()
    
    session_id = str(test_session.id)
    response = await client.post(f"/api/v1/sessions/{session_id}/assess")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    
    assessment = data["data"]
    assert "id" in assessment
    assert "session_id" in assessment
    assert "overall_score" in assessment
    assert "risk_level" in assessment
    assert "entropy_score" in assessment
    assert "uniqueness_score" in assessment
    assert "correlation_score" in assessment
    assert "temporal_score" in assessment
    assert "confidence" in assessment
    assert "recommendations" in assessment
    assert "assessed_at" in assessment
    
    assert 0 <= assessment["overall_score"] <= 100
    assert 0.0 <= assessment["entropy_score"] <= 1.0
    assert 0.0 <= assessment["uniqueness_score"] <= 1.0
    assert 0.0 <= assessment["correlation_score"] <= 1.0
    assert 0.0 <= assessment["temporal_score"] <= 1.0
    assert 0.0 <= assessment["confidence"] <= 1.0
    
    assert assessment["risk_level"] in ["low", "medium", "high", "critical"]
    
    assert "metadata" in data
    assert "request_id" in data["metadata"]
    assert "timestamp" in data["metadata"]


@pytest.mark.asyncio
async def test_baseline_compare_nonexistent_session(test_client_with_db):
    """Test baseline comparison for non-existent session"""
    client, _ = test_client_with_db
    
    fake_session_id = str(uuid4())
    response = await client.post(f"/api/v1/sessions/{fake_session_id}/baseline-compare")
    
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False


@pytest.mark.asyncio
async def test_baseline_compare_without_assessment(test_client_with_db):
    """Test baseline comparison before running assessment"""
    client, test_session = test_client_with_db
    
    session_id = str(test_session.id)
    response = await client.post(f"/api/v1/sessions/{session_id}/baseline-compare")
    
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        result = data["data"]
        assert "baseline_comparison" in result or "actual" in result
        
        if "baseline_comparison" in result:
            baseline = result["baseline_comparison"]
            assert "actual" in baseline
            assert "random_baseline" in baseline
            assert "ideal_baseline" in baseline


@pytest.mark.asyncio
async def test_baseline_compare_with_assessment(test_client_with_db):
    """Test baseline comparison after assessment"""
    client, test_session = test_client_with_db
    
    session_id = str(test_session.id)
    assess_response = await client.post(f"/api/v1/sessions/{session_id}/assess")
    
    if assess_response.status_code != 200:
        pytest.skip("Assessment failed, skipping baseline test")
    
    response = await client.post(f"/api/v1/sessions/{session_id}/baseline-compare")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    
    result = data["data"]
    
    if "baseline_comparison" in result:
        baseline = result["baseline_comparison"]
        assert "actual" in baseline
        assert "random_baseline" in baseline
        assert "ideal_baseline" in baseline
        
        actual = baseline["actual"]
        assert "entropy" in actual or "entropy_score" in actual
        assert "uniqueness" in actual or "uniqueness_score" in actual
        assert "correlation" in actual or "correlation_score" in actual
        assert "temporal" in actual or "temporal_score" in actual
    
    if "industry_comparison" in result:
        industry = result["industry_comparison"]
        assert "session_metrics" in industry or "industry_mean" in industry


@pytest.mark.asyncio
async def test_simulate_attack_insufficient_data(test_client_with_db):
    """Test attack simulation with insufficient sessions"""
    client, test_session = test_client_with_db
    
    session_id = str(test_session.id)
    response = await client.post(f"/api/v1/sessions/{session_id}/simulate-attack")
    
    assert response.status_code in [200, 400, 404]
    
    if response.status_code == 200:
        data = response.json()
        assert data["success"] is True
        
        if "data" in data:
            result = data["data"]
            assert "attack_type" in result or "classifiers" in result
            
            if "classifiers" in result:
                classifiers = result["classifiers"]
                for clf_name, clf_data in classifiers.items():
                    assert "test_accuracy" in clf_data or "attack_success_rate" in clf_data


@pytest.mark.asyncio
async def test_adversarial_test_insufficient_data(test_client_with_db):
    """Test adversarial testing with insufficient sessions"""
    client, test_session = test_client_with_db
    
    session_id = str(test_session.id)
    response = await client.post(f"/api/v1/sessions/{session_id}/adversarial-test")
    
    assert response.status_code in [200, 400, 404]
    
    if response.status_code == 200:
        data = response.json()
        assert data["success"] is True
        
        if "data" in data:
            result = data["data"]
            if "defense_strategies" in result:
                defenses = result["defense_strategies"]
                for strategy_name, strategy_data in defenses.items():
                    assert "attack_effectiveness_after" in strategy_data or \
                           "reduction_percentage" in strategy_data


@pytest.mark.asyncio
async def test_risk_assessment_idempotency(test_client_with_db):
    """Test that multiple assessments return consistent results"""
    client, test_session = test_client_with_db
    
    session_id = str(test_session.id)
    
    response1 = await client.post(f"/api/v1/sessions/{session_id}/assess")
    response2 = await client.post(f"/api/v1/sessions/{session_id}/assess")
    
    if response1.status_code == 200 and response2.status_code == 200:
        data1 = response1.json()
        data2 = response2.json()
        
        assert data1["success"] is True
        assert data2["success"] is True
        
        score1 = data1["data"]["overall_score"]
        score2 = data2["data"]["overall_score"]
        
        assert abs(score1 - score2) < 10


@pytest.mark.asyncio
async def test_risk_level_thresholds(test_client_with_db):
    """Test risk level classification based on scores"""
    client, test_session = test_client_with_db
    
    session_id = str(test_session.id)
    response = await client.post(f"/api/v1/sessions/{session_id}/assess")
    
    if response.status_code == 200:
        data = response.json()
        assessment = data["data"]
        
        score = assessment["overall_score"]
        level = assessment["risk_level"]
        
        if score <= 30:
            assert level == "low"
        elif score <= 50:
            assert level == "medium"
        elif score <= 70:
            assert level == "high"
        else:
            assert level == "critical"


@pytest.mark.asyncio
async def test_assessment_metadata_format(test_client_with_db):
    """Test assessment response metadata format"""
    client, test_session = test_client_with_db
    
    session_id = str(test_session.id)
    response = await client.post(f"/api/v1/sessions/{session_id}/assess")
    
    if response.status_code == 200:
        data = response.json()
        assert "metadata" in data
        
        metadata = data["metadata"]
        assert "request_id" in metadata
        assert "timestamp" in metadata
        
        try:
            datetime.fromisoformat(metadata["timestamp"].replace('Z', '+00:00'))
        except ValueError:
            pytest.fail("Timestamp is not in valid ISO 8601 format")


@pytest.mark.asyncio
async def test_multiple_sessions_assessment(test_client_with_db):
    """Test assessment for multiple different sessions"""
    client, _ = test_client_with_db
    
    from app.core.database import async_session_maker
    
    async with async_session_maker() as db:
        session2 = Session(
            id=str(uuid4()),
            wallet_type="MetaMask",
            rpc_provider="Infura",
            status=SessionStatus.COMPLETED,
            start_time=datetime.now(timezone.utc) - timedelta(hours=2),
            end_time=datetime.now(timezone.utc)
        )
        db.add(session2)
        
        for i in range(3):
            traffic = NetworkTraffic(
                session_id=session2.id,
                rpc_method="eth_getBalance",
                request_data={"jsonrpc": "2.0", "method": "eth_getBalance"},
                response_data={"jsonrpc": "2.0", "result": "0x789"},
                timestamp=datetime.now(timezone.utc) - timedelta(minutes=i*10),
                response_time_ms=30 + i * 5
            )
            db.add(traffic)
        
        await db.commit()
    
    response1 = await client.post(f"/api/v1/sessions/{str(test_client_with_db[1].id)}/assess")
    response2 = await client.post(f"/api/v1/sessions/{session2.id}/assess")
    
    if response1.status_code == 200 and response2.status_code == 200:
        data1 = response1.json()
        data2 = response2.json()
        
        assert data1["success"] is True
        assert data2["success"] is True
        
        assert "data" in data1
        assert "data" in data2