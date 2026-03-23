"""
Integration tests for Dashboard API (Section 3.4)

Tests for:
- GET /dashboard/monitor/status
- GET /dashboard/monitor/leaks/stream
- GET /dashboard/monitor/risk/metrics
- GET /dashboard/reports/timeline
- GET /dashboard/reports/heatmap
- GET /dashboard/charts
- POST /dashboard/comprehensive-report
"""
import pytest
import httpx
from httpx import ASGITransport
from app.main import app
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from app.models import Session, NetworkTraffic, PrivacyLeakEvent, RiskAssessment, SessionStatus
from app.models.dashboard import TimeRange


@pytest.fixture(scope="function")
async def dashboard_test_client(test_session):
    """Create test client for dashboard API tests"""
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client, test_session


@pytest.mark.asyncio
async def test_get_monitor_status(dashboard_test_client):
    """Test monitor status endpoint"""
    client, _ = dashboard_test_client
    
    response = await client.get("/dashboard/monitor/status")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert "data" in data
    
    status = data["data"]
    assert "active_sessions" in status
    assert "total_sessions" in status
    assert "capturing" in status
    assert "today_packets" in status
    assert "today_leaks" in status
    assert "capture_rate" in status
    
    assert isinstance(status["active_sessions"], int)
    assert isinstance(status["total_sessions"], int)
    assert isinstance(status["capturing"], bool)
    assert isinstance(status["today_packets"], int)
    assert isinstance(status["today_leaks"], int)
    assert isinstance(status["capture_rate"], (int, float))
    
    assert "metadata" in data
    assert "request_id" in data["metadata"]
    assert "timestamp" in data["metadata"]


@pytest.mark.asyncio
async def test_get_leak_stream_default_params(dashboard_test_client):
    """Test leak stream with default parameters"""
    client, _ = dashboard_test_client
    
    response = await client.get("/dashboard/monitor/leaks/stream")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert "data" in data
    
    stream = data["data"]
    assert "events" in stream
    assert "stream_position" in stream
    assert "has_more" in stream
    assert "leak_rate" in stream
    
    assert isinstance(stream["events"], list)
    assert isinstance(stream["has_more"], bool)
    
    for event in stream["events"]:
        assert "id" in event
        assert "session_id" in event
        assert "leak_type" in event
        assert "timestamp" in event or "created_at" in event


@pytest.mark.asyncio
async def test_get_leak_stream_custom_params(dashboard_test_client):
    """Test leak stream with custom limit and offset"""
    client, _ = dashboard_test_client
    
    response = await client.get("/dashboard/monitor/leaks/stream?limit=10&offset=5")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    stream = data["data"]
    
    assert len(stream["events"]) <= 10
    
    invalid_response = await client.get("/dashboard/monitor/leaks/stream?limit=200")
    assert invalid_response.status_code == 422


@pytest.mark.asyncio
async def test_get_risk_metrics(dashboard_test_client):
    """Test real-time risk metrics endpoint"""
    client, _ = dashboard_test_client
    
    response = await client.get("/dashboard/monitor/risk/metrics")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert "data" in data
    
    metrics = data["data"]
    assert "current_risk_level" in metrics
    assert "average_risk_score" in metrics
    assert "high_risk_sessions" in metrics
    assert "risk_trend" in metrics
    assert "confidence" in metrics
    assert "last_updated" in metrics
    
    assert metrics["current_risk_level"] in ["low", "medium", "high", "critical"]
    assert 0 <= metrics["average_risk_score"] <= 100
    assert metrics["risk_trend"] in ["increasing", "decreasing", "stable"]
    assert 0.0 <= metrics["confidence"] <= 1.0


@pytest.mark.asyncio
async def test_get_timeline_default_range(dashboard_test_client):
    """Test timeline with default time range"""
    client, _ = dashboard_test_client
    
    response = await client.get("/dashboard/reports/timeline")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert "data" in data
    
    timeline = data["data"]
    assert "events" in timeline
    assert "time_range" in timeline
    assert "total_events" in timeline
    assert "leak_distribution" in timeline
    
    assert isinstance(timeline["events"], list)
    assert isinstance(timeline["total_events"], int)
    
    for event in timeline["events"]:
        assert "timestamp" in event
        assert "event_type" in event
        assert "description" in event


@pytest.mark.asyncio
async def test_get_timeline_custom_range(dashboard_test_client):
    """Test timeline with various time ranges"""
    client, _ = dashboard_test_client
    
    time_ranges = ["last_hour", "last_24h", "last_7d", "last_30d", "last_year"]
    
    for time_range in time_ranges:
        response = await client.get(f"/dashboard/reports/timeline?time_range={time_range}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        timeline = data["data"]
        
        assert "events" in timeline
        assert "time_range" in timeline


@pytest.mark.asyncio
async def test_get_heatmap_valid_types(dashboard_test_client):
    """Test heatmap with valid types"""
    client, _ = dashboard_test_client
    
    heatmap_types = ["timeofday", "method_frequency", "dayofweek"]
    
    for heatmap_type in heatmap_types:
        response = await client.get(f"/dashboard/reports/heatmap?heatmap_type={heatmap_type}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        
        heatmap = data["data"]
        assert "heatmap_type" in heatmap
        assert "row_labels" in heatmap
        assert "col_labels" in heatmap
        assert "cells" in heatmap
        assert "max_value" in heatmap
        assert "min_value" in heatmap
        
        assert isinstance(heatmap["row_labels"], list)
        assert isinstance(heatmap["col_labels"], list)
        assert isinstance(heatmap["cells"], list)
        
        for cell in heatmap["cells"]:
            assert "row_label" in cell
            assert "col_label" in cell
            assert "value" in cell
            assert "count" in cell


@pytest.mark.asyncio
async def test_get_heatmap_invalid_type(dashboard_test_client):
    """Test heatmap with invalid type"""
    client, _ = dashboard_test_client
    
    response = await client.get("/dashboard/reports/heatmap?heatmap_type=invalid_type")
    
    assert response.status_code in [200, 422]
    
    if response.status_code == 200:
        data = response.json()
        heatmap = data["data"]
        assert "heatmap_type" in heatmap


@pytest.mark.asyncio
async def test_get_charts_default_range(dashboard_test_client):
    """Test charts endpoint with default range"""
    client, _ = dashboard_test_client
    
    response = await client.get("/dashboard/charts")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert "data" in data
    
    charts_data = data["data"]
    assert "charts" in charts_data
    
    charts = charts_data["charts"]
    assert isinstance(charts, list)
    
    for chart in charts:
        assert "chart_type" in chart
        assert "title" in chart
        assert "series" in chart


@pytest.mark.asyncio
async def test_get_charts_custom_range(dashboard_test_client):
    """Test charts endpoint with custom time ranges"""
    client, _ = dashboard_test_client
    
    time_ranges = ["last_hour", "last_24h", "last_7d", "last_30d"]
    
    for time_range in time_ranges:
        response = await client.get(f"/dashboard/charts?time_range={time_range}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        assert "charts" in data["data"]


@pytest.mark.asyncio
async def test_get_chart_by_type(dashboard_test_client):
    """Test individual chart by type endpoint"""
    client, _ = dashboard_test_client
    
    chart_types = ["timeline", "pie", "bar", "line"]
    
    for chart_type in chart_types:
        response = await client.get(f"/dashboard/charts/{chart_type}?time_range=last_7d")
        
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert "data" in data
            assert "chart" in data["data"]


@pytest.mark.asyncio
async def test_comprehensive_report_default_range(dashboard_test_client):
    """Test comprehensive report with default time range"""
    client, test_session = dashboard_test_client
    
    response = await client.post("/dashboard/comprehensive-report")
    
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        report = data["data"]
        assert "report_metadata" in report
        assert "results" in report
        
        metadata = report["report_metadata"]
        assert "generated_at" in metadata
        assert "time_range" in metadata
        assert "num_sessions_tested" in metadata


@pytest.mark.asyncio
async def test_comprehensive_report_custom_ranges(dashboard_test_client):
    """Test comprehensive report with various time ranges"""
    client, _ = dashboard_test_client
    
    time_ranges = ["last_hour", "last_24h", "last_7d", "last_30d"]
    
    for time_range in time_ranges:
        response = await client.post(f"/dashboard/comprehensive-report?time_range={time_range}")
        
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            
            report = data["data"]
            assert "report_metadata" in report
            assert report["report_metadata"]["time_range"] == time_range


@pytest.mark.asyncio
async def test_comprehensive_report_no_sessions(dashboard_test_client):
    """Test comprehensive report when no sessions exist in time range"""
    client, _ = dashboard_test_client
    
    response = await client.post("/dashboard/comprehensive-report?time_range=last_hour")
    
    assert response.status_code in [200, 404]
    
    if response.status_code == 404:
        data = response.json()
        assert "detail" in data
        assert "code" in data["detail"]
        assert data["detail"]["code"] == "NO_SESSIONS_FOUND"


@pytest.mark.asyncio
async def test_dashboard_endpoints_consistency(dashboard_test_client):
    """Test that dashboard endpoints return consistent data formats"""
    client, _ = dashboard_test_client
    
    endpoints = [
        "/dashboard/monitor/status",
        "/dashboard/monitor/leaks/stream",
        "/dashboard/monitor/risk/metrics",
        "/dashboard/reports/timeline",
    ]
    
    for endpoint in endpoints:
        response = await client.get(endpoint)
        
        if response.status_code == 200:
            data = response.json()
            
            assert "success" in data
            assert "metadata" in data
            assert "request_id" in data["metadata"]
            assert "timestamp" in data["metadata"]


@pytest.mark.asyncio
async def test_dashboard_with_populated_data(dashboard_test_client):
    """Test dashboard endpoints with populated test data"""
    client, test_session = dashboard_test_client
    
    from app.core.database import async_session_maker
    
    async with async_session_maker() as db:
        for i in range(10):
            traffic = NetworkTraffic(
                session_id=test_session.id,
                rpc_method=f"eth_method_{i % 3}",
                request_data={"jsonrpc": "2.0", "method": f"method_{i}"},
                response_data={"jsonrpc": "2.0", "result": f"result_{i}"},
                timestamp=datetime.now(timezone.utc) - timedelta(minutes=i*5),
                response_time_ms=20 + i * 5
            )
            db.add(traffic)
        
        for i in range(3):
            leak = PrivacyLeakEvent(
                session_id=test_session.id,
                leak_type=["identity", "behavior", "location"][i % 3],
                method_name="eth_sendTransaction",
                description=f"Test leak {i}",
                confidence=0.8 + i * 0.05,
                timestamp=datetime.now(timezone.utc) - timedelta(minutes=i*10)
            )
            db.add(leak)
        
        assessment = RiskAssessment(
            session_id=test_session.id,
            overall_score=65,
            risk_level="medium",
            entropy_score=0.7,
            uniqueness_score=0.6,
            correlation_score=0.5,
            temporal_score=0.65,
            confidence=0.85,
            assessed_at=datetime.now(timezone.utc)
        )
        db.add(assessment)
        
        await db.commit()
    
    endpoints = [
        "/dashboard/monitor/status",
        "/dashboard/monitor/leaks/stream",
        "/dashboard/monitor/risk/metrics",
        "/dashboard/reports/timeline",
        "/dashboard/reports/heatmap?heatmap_type=timeofday",
        "/dashboard/charts",
    ]
    
    for endpoint in endpoints:
        response = await client.get(endpoint)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


@pytest.mark.asyncio
async def test_dashboard_error_handling(dashboard_test_client):
    """Test dashboard error handling"""
    client, _ = dashboard_test_client
    
    invalid_endpoints = [
        "/dashboard/monitor/leaks/stream?limit=-1",
        "/dashboard/monitor/leaks/stream?limit=0",
        "/dashboard/reports/timeline?time_range=invalid",
    ]
    
    for endpoint in invalid_endpoints:
        response = await client.get(endpoint)
        assert response.status_code in [200, 422]


@pytest.mark.asyncio
async def test_dashboard_response_times(dashboard_test_client):
    """Test dashboard endpoint response times"""
    client, _ = dashboard_test_client
    
    import time
    
    endpoints = [
        "/dashboard/monitor/status",
        "/dashboard/monitor/leaks/stream",
        "/dashboard/monitor/risk/metrics",
    ]
    
    for endpoint in endpoints:
        start = time.time()
        response = await client.get(endpoint)
        elapsed = time.time() - start
        
        assert elapsed < 0.5, f"Endpoint {endpoint} took {elapsed:.3f}s"
        assert response.status_code == 200