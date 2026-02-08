"""
Tests for the view_file endpoint
"""
import os
from unittest.mock import Mock, patch
import pytest


@pytest.fixture(autouse=True)
def mock_config():
    """Mock the config settings before any imports"""
    mock_settings = Mock()
    mock_settings.DIR_LOCATION = "/tmp/test"
    mock_settings.admin_email = "test@test.com"
    mock_settings.SECRET_KEY = "test_secret"
    mock_settings.DATABASE_URL = "sqlite:///:memory:"
    mock_settings.HTTP_AUTH_USERNAME = "test"
    mock_settings.HTTP_AUTH_PASSWORD = "test"
    
    with patch('app.core.config.Settings', return_value=mock_settings):
        with patch('app.api.file.view_file.config', mock_settings):
            yield mock_settings


@pytest.fixture
def mock_user():
    """Create a mock user"""
    user = Mock()
    user.root_foldername = "test_user"
    return user


@pytest.fixture
def test_dir(tmp_path, mock_config):
    """Create a temporary test directory structure"""
    data_dir = tmp_path / "data" / "test_user"
    data_dir.mkdir(parents=True)
    mock_config.DIR_LOCATION = str(tmp_path)
    return tmp_path, data_dir


def test_file_too_large(test_dir, mock_user):
    """Test that files over 30MB return appropriate error"""
    from app.api.file.view_file import view_file
    from fastapi import HTTPException
    
    tmp_path, data_dir = test_dir
    
    # Create a file larger than 30MB
    large_file = data_dir / "large_video.mp4"
    # Create a 31MB file (just over the limit)
    with open(large_file, 'wb') as f:
        f.write(b'0' * (31 * 1024 * 1024))
    
    with pytest.raises(HTTPException) as exc_info:
        import asyncio
        asyncio.run(view_file("large_video.mp4", mock_user))
    
    # Check status code
    assert exc_info.value.status_code == 413
    
    # Check response details
    detail = exc_info.value.detail
    assert detail["error"] == "file_too_large"
    assert "too large for inline viewing" in detail["message"]
    assert detail["file_size"] > 30 * 1024 * 1024
    assert detail["size_limit"] == 30 * 1024 * 1024
    assert "download_url" in detail
    assert detail["filename"] == "large_video.mp4"


def test_unsupported_file_type(test_dir, mock_user):
    """Test that unsupported file types return appropriate error"""
    from app.api.file.view_file import view_file
    from fastapi import HTTPException
    
    tmp_path, data_dir = test_dir
    
    # Create a small .exe file
    exe_file = data_dir / "installer.exe"
    with open(exe_file, 'wb') as f:
        f.write(b'MZ')  # DOS header signature
    
    with pytest.raises(HTTPException) as exc_info:
        import asyncio
        asyncio.run(view_file("installer.exe", mock_user))
    
    # Check status code
    assert exc_info.value.status_code == 415
    
    # Check response details
    detail = exc_info.value.detail
    assert detail["error"] == "unsupported_file_type"
    assert "cannot be viewed in browser" in detail["message"]
    assert detail["file_extension"] == ".exe"
    assert "download_url" in detail
    assert detail["filename"] == "installer.exe"


def test_viewable_file_small_size(test_dir, mock_user):
    """Test that small viewable files work correctly"""
    from app.api.file.view_file import view_file
    
    tmp_path, data_dir = test_dir
    
    # Create a small text file
    text_file = data_dir / "test.txt"
    with open(text_file, 'w') as f:
        f.write("Hello, World!")
    
    import asyncio
    response = asyncio.run(view_file("test.txt", mock_user))
    
    # Check that we got a FileResponse (not an exception)
    assert response is not None


def test_download_url_format(test_dir, mock_user):
    """Test that download URLs are correctly formatted with URL encoding"""
    from app.api.file.view_file import view_file
    from fastapi import HTTPException
    
    tmp_path, data_dir = test_dir
    
    # Create a file with special characters in name
    special_file = data_dir / "test file with spaces.exe"
    with open(special_file, 'wb') as f:
        f.write(b'test')
    
    with pytest.raises(HTTPException) as exc_info:
        import asyncio
        asyncio.run(view_file("test file with spaces.exe", mock_user))
    
    # Check that download URL is properly encoded
    detail = exc_info.value.detail
    assert "download_url" in detail
    # Spaces should be URL encoded
    assert "test%20file%20with%20spaces.exe" in detail["download_url"]


def test_file_size_exactly_at_limit(test_dir, mock_user):
    """Test file exactly at 30MB limit (should pass)"""
    from app.api.file.view_file import view_file
    
    tmp_path, data_dir = test_dir
    
    # Create a file exactly 30MB
    limit_file = data_dir / "exactly_30mb.mp4"
    with open(limit_file, 'wb') as f:
        f.write(b'0' * (30 * 1024 * 1024))
    
    import asyncio
    # Should not raise an exception
    response = asyncio.run(view_file("exactly_30mb.mp4", mock_user))
    assert response is not None


def test_file_size_just_over_limit(test_dir, mock_user):
    """Test file just over 30MB limit (should fail)"""
    from app.api.file.view_file import view_file
    from fastapi import HTTPException
    
    tmp_path, data_dir = test_dir
    
    # Create a file just over 30MB (30MB + 1 byte)
    over_file = data_dir / "just_over.mp4"
    with open(over_file, 'wb') as f:
        f.write(b'0' * (30 * 1024 * 1024 + 1))
    
    with pytest.raises(HTTPException) as exc_info:
        import asyncio
        asyncio.run(view_file("just_over.mp4", mock_user))
    
    # Check status code
    assert exc_info.value.status_code == 413
