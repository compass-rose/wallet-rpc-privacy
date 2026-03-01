"""
Integration tests for API endpoints (lightweight, no database dependency)
"""
import pytest
import httpx
from httpx import ASGITransport
from app.main import app


@pytest.fixture(scope="function")
async def test_client():
    """Create test client without database dependency"""
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_root_endpoint(test_client):
    """Test root endpoint"""
    response = await test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.asyncio
async def test_health_endpoint(test_client):
    """Test health check endpoint"""
    response = await test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_list_rules(test_client):
    """Test listing detection rules"""
    response = await test_client.get("/api/v1/rules")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "rules" in data["data"]


@pytest.mark.asyncio
async def test_get_rules_summary(test_client):
    """Test rules summary"""
    response = await test_client.get("/api/v1/rules/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "total" in data["data"]
