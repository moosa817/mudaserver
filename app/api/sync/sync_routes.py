from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.dependencies import get_current_user
from app.models.user import User
from pydantic import BaseModel
import os
from app.core.config import config
from app.services.sync.hash_utils import calculate_file_hash, get_file_metadata
from typing import List, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

syncrouter = APIRouter()

# Conflict detection threshold in seconds
# If file modification times differ by less than this, it's considered a conflict
# 60 seconds allows for minor clock skew between client and server
CONFLICT_THRESHOLD_SECONDS = 60


# Pydantic models
class FileHashResponse(BaseModel):
    file_path: str
    hash: str
    size: int
    modified_at: str
    exists: bool


class FileCheckItem(BaseModel):
    path: str
    local_hash: str
    local_modified: str


class BatchSyncCheckRequest(BaseModel):
    files: List[FileCheckItem]


class SyncStatusResult(BaseModel):
    path: str
    status: str
    server_hash: Optional[str]
    server_modified: Optional[str]


class BatchSyncCheckResponse(BaseModel):
    results: List[SyncStatusResult]


class FileItem(BaseModel):
    path: str
    hash: Optional[str]
    size: Optional[int]
    modified_at: str
    type: str


class ListAllFilesResponse(BaseModel):
    files: List[FileItem]
    total_files: int
    total_size: int


class DeleteFileResponse(BaseModel):
    success: bool
    message: str
    path: str


def validate_path_security(file_path: str, base_path: str) -> str:
    """
    Validate that the file path is within the user's directory.
    Returns the full path if valid, raises HTTPException if not.
    """
    full_path = os.path.join(base_path, file_path)
    full_path = os.path.realpath(full_path)
    base_path = os.path.realpath(base_path)
    
    try:
        if os.path.commonpath([full_path, base_path]) != base_path:
            raise HTTPException(status_code=403, detail="Access denied: Path is outside user directory")
    except ValueError:
        # Different drives on Windows or other path issues
        raise HTTPException(status_code=403, detail="Access denied: Invalid path")
    
    return full_path


def parse_iso_datetime(timestamp_str: str) -> datetime:
    """
    Parse ISO datetime string, handling both 'Z' suffix and timezone offsets.
    
    Args:
        timestamp_str: ISO format datetime string
    
    Returns:
        datetime object with timezone
    """
    return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))


@syncrouter.get("/file-hash", response_model=FileHashResponse)
async def get_file_hash(
    file_path: str = Query(..., description="Relative path of the file within user's storage"),
    user: User = Depends(get_current_user)
):
    """
    Get the hash and metadata of a file on the server.
    """
    try:
        file_path = file_path.strip()
        base_path = os.path.join(config.DIR_LOCATION, "data", user.root_foldername)
        full_path = validate_path_security(file_path, base_path)
        
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        if not os.path.isfile(full_path):
            raise HTTPException(status_code=400, detail="Path is not a file")
        
        metadata = get_file_metadata(full_path)
        
        return FileHashResponse(
            file_path=file_path,
            hash=metadata["hash"],
            size=metadata["size"],
            modified_at=metadata["modified_at"],
            exists=metadata["exists"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file hash: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get file hash")


@syncrouter.post("/check", response_model=BatchSyncCheckResponse)
async def batch_sync_check(
    request: BatchSyncCheckRequest,
    user: User = Depends(get_current_user)
):
    """
    Check sync status for multiple files at once.
    """
    try:
        base_path = os.path.join(config.DIR_LOCATION, "data", user.root_foldername)
        results = []
        
        for file_item in request.files:
            try:
                file_path = file_item.path.strip()
                full_path = validate_path_security(file_path, base_path)
                
                if not os.path.exists(full_path):
                    # File doesn't exist on server
                    results.append(SyncStatusResult(
                        path=file_path,
                        status="local_only",
                        server_hash=None,
                        server_modified=None
                    ))
                    continue
                
                if not os.path.isfile(full_path):
                    # Path is a directory, skip
                    continue
                
                # Get server file metadata
                metadata = get_file_metadata(full_path)
                server_hash = metadata["hash"]
                server_modified = metadata["modified_at"]
                
                # Parse modification times
                local_modified_dt = parse_iso_datetime(file_item.local_modified)
                server_modified_dt = parse_iso_datetime(server_modified)
                
                # Determine sync status
                if server_hash == file_item.local_hash:
                    status = "in_sync"
                else:
                    # Hashes differ, check modification times
                    time_diff = abs((server_modified_dt - local_modified_dt).total_seconds())
                    
                    if time_diff < CONFLICT_THRESHOLD_SECONDS:
                        status = "conflict"
                    elif server_modified_dt > local_modified_dt:
                        status = "server_newer"
                    else:
                        status = "local_newer"
                
                results.append(SyncStatusResult(
                    path=file_path,
                    status=status,
                    server_hash=server_hash,
                    server_modified=server_modified
                ))
            
            except HTTPException:
                # Path validation failed, skip this file
                continue
            except Exception as e:
                logger.error(f"Error checking file {file_item.path}: {e}")
                continue
        
        return BatchSyncCheckResponse(results=results)
    
    except Exception as e:
        logger.error(f"Error in batch sync check: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to perform batch sync check")


@syncrouter.get("/list-all", response_model=ListAllFilesResponse)
async def list_all_files(
    folder_path: Optional[str] = Query("", description="Limit to a specific folder, defaults to root"),
    user: User = Depends(get_current_user)
):
    """
    List all files in the user's storage with their hashes and metadata.
    """
    try:
        base_path = os.path.join(config.DIR_LOCATION, "data", user.root_foldername)
        
        # Validate folder path
        if folder_path:
            folder_path = folder_path.strip()
            start_path = validate_path_security(folder_path, base_path)
        else:
            start_path = base_path
        
        if not os.path.exists(start_path):
            raise HTTPException(status_code=404, detail="Folder not found")
        
        files = []
        total_files = 0
        total_size = 0
        
        # Walk through directory tree
        for root, dirs, filenames in os.walk(start_path):
            # Calculate relative path from base_path
            rel_root = os.path.relpath(root, base_path)
            if rel_root == ".":
                rel_root = ""
            
            # Add directories
            for dirname in dirs:
                dir_rel_path = os.path.join(rel_root, dirname) if rel_root else dirname
                dir_full_path = os.path.join(root, dirname)
                
                try:
                    stat_info = os.stat(dir_full_path)
                    modified_at = datetime.fromtimestamp(stat_info.st_mtime, tz=timezone.utc)
                    
                    files.append(FileItem(
                        path=dir_rel_path,
                        hash=None,
                        size=None,
                        modified_at=modified_at.isoformat(),
                        type="folder"
                    ))
                except Exception as e:
                    logger.warning(f"Error accessing directory {dir_rel_path}: {e}")
                    continue
            
            # Add files
            for filename in filenames:
                file_rel_path = os.path.join(rel_root, filename) if rel_root else filename
                file_full_path = os.path.join(root, filename)
                
                try:
                    metadata = get_file_metadata(file_full_path)
                    if metadata:
                        files.append(FileItem(
                            path=file_rel_path,
                            hash=metadata["hash"],
                            size=metadata["size"],
                            modified_at=metadata["modified_at"],
                            type="file"
                        ))
                        total_files += 1
                        total_size += metadata["size"]
                except Exception as e:
                    logger.warning(f"Error accessing file {file_rel_path}: {e}")
                    continue
        
        return ListAllFilesResponse(
            files=files,
            total_files=total_files,
            total_size=total_size
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing files: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list files")


@syncrouter.delete("/delete", response_model=DeleteFileResponse)
async def delete_file_sync(
    file_path: str = Query(..., description="Relative path of the file to delete"),
    user: User = Depends(get_current_user)
):
    """
    Delete a file that was deleted locally (for two-way sync).
    """
    try:
        file_path = file_path.strip()
        base_path = os.path.join(config.DIR_LOCATION, "data", user.root_foldername)
        full_path = validate_path_security(file_path, base_path)
        
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        if not os.path.isfile(full_path):
            raise HTTPException(status_code=400, detail="Path is not a file")
        
        os.remove(full_path)
        
        return DeleteFileResponse(
            success=True,
            message="File deleted successfully",
            path=file_path
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete file")
