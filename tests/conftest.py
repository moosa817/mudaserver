"""
Pytest configuration file
"""
import os
import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment variables before any imports"""
    os.environ["admin_email"] = "test@example.com"
    os.environ["SECRET_KEY"] = "test_secret_key_123"
    os.environ["DIR_LOCATION"] = "/tmp/test"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["HTTP_AUTH_USERNAME"] = "testuser"
    os.environ["HTTP_AUTH_PASSWORD"] = "testpass"
