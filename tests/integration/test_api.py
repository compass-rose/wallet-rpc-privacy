"""
Integration tests for API endpoints
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
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
async def client():
    """Create test client"""
    # Override database dependency
    app.dependency_overrides[get_session] = get_test_session

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    # Clean up
    app.dependency_overrides.clear()
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    """Create and drop test database tables"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test root endpoint"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Test health check endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_session(client):
    """Test session creation"""
    response = await client.post(
        "/api/v1/sessions",
        json={
            "wallet_type": "MetaMask",
            "rpc_provider": "https://mainnet.infura.io/v3/test"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "id" in data["data"]
    assert data["data"]["wallet_type"] == "MetaMask"


@pytest.mark.asyncio
async def test_get_session(client):
    """Test getting a session"""
    # Create a session first
    create_response = await client.post(
        "/api/v1/sessions",
        json={
            "wallet_type": "MetaMask",
            "rpc_provider": "https://mainnet.infura.io/v3/test"
        }
    )
    session_id = create_response.json()["data"]["id"]

    # Get the session
    response = await client.get(f"/api/v1/sessions/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == session_id


@pytest.mark.asyncio
async def test_get_session_not_found(client):
    """Test getting non-existent session"""
    response = await client.get("/api/v1/sessions/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_sessions(client):
    """Test listing sessions"""
    # Create two sessions
    await client.post(
        "/api/v1/sessions",
        json={"wallet_type": "MetaMask", "rpc_provider": "https://mainnet.infura.io/v3/test"}
    )
    await client.post(
        "/api/v1/sessions",
        json={"wallet_type": "WalletConnect", "rpc_provider": "https://mainnet.infura.io/v3/test"}
    )

    response = await client.get("/api/v1/sessions")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["sessions"]) >= 2


@pytest.mark.asyncio
async def test_start_capture(client):
    """Test starting traffic capture"""
    # Create a session
    create_response = await client.post(
        "/api/v1/sessions",
        json={
            "wallet_type": "MetaMask",
            "rpc_provider": "https://mainnet.infura.io/v3/test"
        }
    )
    session_id = create_response.json()["data"]["id"]

    # Start capture
    response = await client.post(
        f"/api/v1/sessions/{session_id}/traffic/start",
        params={"packet_count": 10}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["active"] is True


@pytest.mark.asyncio
async def test_get_traffic(client):
    """Test getting traffic records"""
    # Create and capture
    create_response = await client.post(
        "/api/v1/sessions",
        json={
            "wallet_type": "MetaMask",
            "rpc_provider": "https://mainnet.infura.io/v3/test"
        }
    )
    session_id = create_response.json()["data"]["id"]

    await client.post(
        f"/api/v1/sessions/{session_id}/traffic/start",
        params={"packet_count": 20}
    )

    # Get traffic
    response = await client.get(f"/api/v1/sessions/{session_id}/traffic")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["traffic"]) > 0


@pytest.mark.asyncio
async def test_get_analytics_summary(client):
    """Test analytics summary"""
    response = await client.get("/api/v1/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "total_sessions" in data["data"]


@pytest.mark.asyncio
async def test_list_rules(client):
    """Test listing detection rules"""
    response = await client.get("/api/v1/rules")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "rules" in data["data"]
    assert len(data["data"]["rules"]) >= 10


@pytest.mark.asyncio
async def test_get_rules_summary(client):
    """Test rules summary"""
    response = await client.get("/api/v1/rules/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "total" in data["data"]


@pytest.mark.asyncio
async def test_delete_session(client):
    """Test deleting a session"""
    # Create a session
    create_response = await client.post(
        "/api/v1/sessions",
        json={
            "wallet_type": "MetaMask",
            "rpc_provider": "https://mainnet.infura.io/v3/test"
        }
    )
    session_id = create_response.json()["data"]["id"]

    # Delete the session
    response = await client.delete(f"/api/v1/sessions/{session_id}")
    assert response.status_code == 200

    # Verify it's deleted
    get_response = await client.get(f"/api/v1/sessions/{session_id}")
    assert get_response.status_code == 404
