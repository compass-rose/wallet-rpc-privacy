"""
Unit tests for app/main.py
"""
import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from fastapi import Request


class TestMainApp:
    """Test main application"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from app.main import app
        return TestClient(app)

    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["status"] == "healthy"

    def test_health_check_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data

    def test_cors_middleware_configured(self, client):
        """Test that CORS middleware is properly configured"""
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )

        # CORS should allow the request
        assert response.status_code in [200, 204] or "access-control-allow-origin" in response.headers

    def test_app_creation(self):
        """Test that FastAPI app is created correctly"""
        from app.main import app

        assert app is not None
        assert app.title == "Wallet / RPC Privacy Leakage Measurement"
        assert app.version == "1.0.0"
        assert app.docs_url == "/docs"
        assert app.redoc_url == "/redoc"

    def test_routers_included(self):
        """Test that all routers are properly included"""
        from app.main import app

        paths = [route.path for route in app.routes if hasattr(route, 'path')]

        # Check that major route groups are included
        assert any("/api/v1" in path for path in paths)
        assert any("/sessions" in path or path.startswith("/api/v1/sessions") for path in paths)

    @patch.dict('os.environ', {'LOG_LEVEL': 'DEBUG'}, clear=False)
    def test_settings_loaded(self):
        """Test that settings are properly loaded"""
        from app.main import settings

        assert settings is not None
        assert hasattr(settings, 'cors_origins')
        assert hasattr(settings, 'log_level')
