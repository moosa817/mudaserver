"""
Tests for the sync API endpoints
"""
import os
import tempfile
from unittest.mock import Mock, patch
import pytest
from datetime import datetime, timezone, timedelta


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
        with patch('app.api.sync.sync_routes.config', mock_settings):
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


def run_async(coro):
    """Helper to run async functions in tests"""
    import asyncio
    return asyncio.run(coro)


def test_get_file_hash_success(test_dir, mock_user):
    """Test getting hash of an existing file"""
    from app.api.sync.sync_routes import get_file_hash
    
    tmp_path, data_dir = test_dir
    
    # Create a test file
    test_file = data_dir / "test.txt"
    test_content = b"Hello, World!"
    with open(test_file, 'wb') as f:
        f.write(test_content)
    
    response = run_async(get_file_hash("test.txt", mock_user))
    
    assert response.file_path == "test.txt"
    assert response.exists is True
    assert len(response.hash) == 32  # MD5 hash length
    assert response.size == len(test_content)
    assert response.modified_at is not None


def test_get_file_hash_not_found(test_dir, mock_user):
    """Test getting hash of non-existent file"""
    from app.api.sync.sync_routes import get_file_hash
    from fastapi import HTTPException
    
    tmp_path, data_dir = test_dir
    
    with pytest.raises(HTTPException) as exc_info:
        run_async(get_file_hash("nonexistent.txt", mock_user))
    
    assert exc_info.value.status_code == 404


def test_get_file_hash_path_traversal(test_dir, mock_user):
    """Test path traversal prevention"""
    from app.api.sync.sync_routes import get_file_hash
    from fastapi import HTTPException
    
    tmp_path, data_dir = test_dir
    
    # Try to access file outside user directory
    with pytest.raises(HTTPException) as exc_info:
        run_async(get_file_hash("../../../etc/passwd", mock_user))
    
    assert exc_info.value.status_code == 403
    assert "Access denied" in str(exc_info.value.detail)


def test_batch_sync_check_in_sync(test_dir, mock_user):
    """Test batch sync check when files are in sync"""
    from app.api.sync.sync_routes import batch_sync_check, BatchSyncCheckRequest, FileCheckItem
    from app.services.sync.hash_utils import calculate_file_hash
    
    tmp_path, data_dir = test_dir
    
    # Create a test file
    test_file = data_dir / "test.txt"
    with open(test_file, 'wb') as f:
        f.write(b"Hello, World!")
    
    # Calculate its hash
    file_hash = calculate_file_hash(str(test_file))
    modified_time = datetime.fromtimestamp(os.stat(test_file).st_mtime, tz=timezone.utc)
    
    request = BatchSyncCheckRequest(files=[
        FileCheckItem(
            path="test.txt",
            local_hash=file_hash,
            local_modified=modified_time.isoformat()
        )
    ])
    
    response = run_async(batch_sync_check(request, mock_user))
    
    assert len(response.results) == 1
    assert response.results[0].path == "test.txt"
    assert response.results[0].status == "in_sync"
    assert response.results[0].server_hash == file_hash


def test_batch_sync_check_local_only(test_dir, mock_user):
    """Test batch sync check when file exists only locally"""
    from app.api.sync.sync_routes import batch_sync_check, BatchSyncCheckRequest, FileCheckItem
    
    tmp_path, data_dir = test_dir
    
    request = BatchSyncCheckRequest(files=[
        FileCheckItem(
            path="local_only.txt",
            local_hash="abc123",
            local_modified=datetime.now(timezone.utc).isoformat()
        )
    ])
    
    response = run_async(batch_sync_check(request, mock_user))
    
    assert len(response.results) == 1
    assert response.results[0].path == "local_only.txt"
    assert response.results[0].status == "local_only"
    assert response.results[0].server_hash is None


def test_batch_sync_check_server_newer(test_dir, mock_user):
    """Test batch sync check when server file is newer"""
    from app.api.sync.sync_routes import batch_sync_check, BatchSyncCheckRequest, FileCheckItem
    
    tmp_path, data_dir = test_dir
    
    # Create a test file
    test_file = data_dir / "test.txt"
    with open(test_file, 'wb') as f:
        f.write(b"Hello, World!")
    
    # Use an old local modified time
    old_time = datetime.now(timezone.utc) - timedelta(hours=2)
    
    request = BatchSyncCheckRequest(files=[
        FileCheckItem(
            path="test.txt",
            local_hash="different_hash",
            local_modified=old_time.isoformat()
        )
    ])
    
    response = run_async(batch_sync_check(request, mock_user))
    
    assert len(response.results) == 1
    assert response.results[0].path == "test.txt"
    assert response.results[0].status == "server_newer"


def test_batch_sync_check_local_newer(test_dir, mock_user):
    """Test batch sync check when local file is newer"""
    from app.api.sync.sync_routes import batch_sync_check, BatchSyncCheckRequest, FileCheckItem
    
    tmp_path, data_dir = test_dir
    
    # Create a test file
    test_file = data_dir / "test.txt"
    with open(test_file, 'wb') as f:
        f.write(b"Hello, World!")
    
    # Use a future local modified time
    future_time = datetime.now(timezone.utc) + timedelta(hours=2)
    
    request = BatchSyncCheckRequest(files=[
        FileCheckItem(
            path="test.txt",
            local_hash="different_hash",
            local_modified=future_time.isoformat()
        )
    ])
    
    response = run_async(batch_sync_check(request, mock_user))
    
    assert len(response.results) == 1
    assert response.results[0].path == "test.txt"
    assert response.results[0].status == "local_newer"


def test_list_all_files(test_dir, mock_user):
    """Test listing all files"""
    from app.api.sync.sync_routes import list_all_files
    
    tmp_path, data_dir = test_dir
    
    # Create a directory structure
    (data_dir / "subfolder").mkdir()
    with open(data_dir / "file1.txt", 'w') as f:
        f.write("File 1")
    with open(data_dir / "file2.txt", 'w') as f:
        f.write("File 2")
    with open(data_dir / "subfolder" / "file3.txt", 'w') as f:
        f.write("File 3")
    
    response = run_async(list_all_files("", mock_user))
    
    # Should have 1 folder and 3 files
    assert response.total_files == 3
    assert len(response.files) == 4  # 1 folder + 3 files
    
    # Check that we have both files and folders
    file_types = [item.type for item in response.files]
    assert "file" in file_types
    assert "folder" in file_types


def test_list_all_files_specific_folder(test_dir, mock_user):
    """Test listing files in a specific folder"""
    from app.api.sync.sync_routes import list_all_files
    
    tmp_path, data_dir = test_dir
    
    # Create a directory structure
    (data_dir / "subfolder").mkdir()
    with open(data_dir / "file1.txt", 'w') as f:
        f.write("File 1")
    with open(data_dir / "subfolder" / "file2.txt", 'w') as f:
        f.write("File 2")
    
    response = run_async(list_all_files("subfolder", mock_user))
    
    # Should only have 1 file in subfolder
    assert response.total_files == 1
    assert len(response.files) == 1


def test_delete_file_sync_success(test_dir, mock_user):
    """Test deleting a file"""
    from app.api.sync.sync_routes import delete_file_sync
    
    tmp_path, data_dir = test_dir
    
    # Create a test file
    test_file = data_dir / "to_delete.txt"
    with open(test_file, 'w') as f:
        f.write("Delete me")
    
    assert test_file.exists()
    
    response = run_async(delete_file_sync("to_delete.txt", mock_user))
    
    assert response.success is True
    assert response.path == "to_delete.txt"
    assert not test_file.exists()


def test_delete_file_sync_not_found(test_dir, mock_user):
    """Test deleting non-existent file"""
    from app.api.sync.sync_routes import delete_file_sync
    from fastapi import HTTPException
    
    tmp_path, data_dir = test_dir
    
    with pytest.raises(HTTPException) as exc_info:
        run_async(delete_file_sync("nonexistent.txt", mock_user))
    
    assert exc_info.value.status_code == 404


def test_delete_file_sync_path_traversal(test_dir, mock_user):
    """Test path traversal prevention in delete"""
    from app.api.sync.sync_routes import delete_file_sync
    from fastapi import HTTPException
    
    tmp_path, data_dir = test_dir
    
    # Try to delete file outside user directory
    with pytest.raises(HTTPException) as exc_info:
        run_async(delete_file_sync("../../../etc/passwd", mock_user))
    
    assert exc_info.value.status_code == 403


def test_hash_calculation_consistency(test_dir):
    """Test that hash calculation is consistent"""
    from app.services.sync.hash_utils import calculate_file_hash
    
    tmp_path, data_dir = test_dir
    
    # Create a test file
    test_file = data_dir / "test.txt"
    with open(test_file, 'wb') as f:
        f.write(b"Test content")
    
    # Calculate hash multiple times
    hash1 = calculate_file_hash(str(test_file))
    hash2 = calculate_file_hash(str(test_file))
    
    assert hash1 == hash2


def test_hash_calculation_different_algorithms(test_dir):
    """Test hash calculation with different algorithms"""
    from app.services.sync.hash_utils import calculate_file_hash
    
    tmp_path, data_dir = test_dir
    
    # Create a test file
    test_file = data_dir / "test.txt"
    with open(test_file, 'wb') as f:
        f.write(b"Test content")
    
    md5_hash = calculate_file_hash(str(test_file), "md5")
    sha256_hash = calculate_file_hash(str(test_file), "sha256")
    
    assert len(md5_hash) == 32  # MD5 is 128 bits = 32 hex chars
    assert len(sha256_hash) == 64  # SHA256 is 256 bits = 64 hex chars
    assert md5_hash != sha256_hash


def test_get_file_metadata(test_dir):
    """Test getting file metadata"""
    from app.services.sync.hash_utils import get_file_metadata
    
    tmp_path, data_dir = test_dir
    
    # Create a test file
    test_file = data_dir / "test.txt"
    with open(test_file, 'wb') as f:
        f.write(b"Test content")
    
    metadata = get_file_metadata(str(test_file))
    
    assert metadata is not None
    assert "hash" in metadata
    assert "size" in metadata
    assert "modified_at" in metadata
    assert "exists" in metadata
    assert metadata["exists"] is True
    assert metadata["size"] == 12  # "Test content" is 12 bytes


def test_get_file_metadata_nonexistent(test_dir):
    """Test getting metadata of non-existent file"""
    from app.services.sync.hash_utils import get_file_metadata
    
    tmp_path, data_dir = test_dir
    
    metadata = get_file_metadata(str(data_dir / "nonexistent.txt"))
    
    assert metadata is None
