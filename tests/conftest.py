"""
Pytest fixtures and configuration

Auto-loads test environment variables from .env.test
"""
import os
from dotenv import load_dotenv

# Auto-load .env.test file for database integration tests
# Note: .env.test contains TEST_DATABASE_URL and other test-specific settings
env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env.test")
load_dotenv(env_file, override=True)
