"""
Unit tests for configuration
"""
import pytest
from app.core.config import get_settings, Settings


def test_settings_singleton():
    """Test that get_settings returns same instance"""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2


def test_settings_default_values():
    """Test default settings values"""
    settings = get_settings()
    assert settings.log_level == "INFO"
    assert settings.traffic_provider == "mock"
    assert settings.mock_traffic_count == 500


def test_settings_database_url():
    """Test database URL configuration"""
    settings = get_settings()
    assert settings.database_url is not None
    assert "mysql" in settings.database_url.lower()
