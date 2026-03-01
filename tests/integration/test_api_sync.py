"""
Integration tests for API endpoints (using TestClient)
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.models.base import Base
from app.core.database import get_session


# Test database URL for testing
TEST_DATABASE_URL = "mysql+aiomysql://root:password@localhost:3306/wallet_privacy_test"


# Override database dependency for tests
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_maker = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)


async def get_test_session():
    async with test_session_maker() as session:
        yield session


@pytest.fixture(scope="function")
def client():
    """Create test client"""
    app.dependency_overrides[get_session] = get_test_session

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_list_rules(client):
    """Test listing detection rules"""
    response = client.get("/api/v1/rules")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "rules" in data["data"]
    assert len(data["data"]["rules"]) >= 10


def test_get_rules_summary(client):
    """Test rules summary"""
    response = client.get("/api/v1/rules/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "total" in data["data"]
