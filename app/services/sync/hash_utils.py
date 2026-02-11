import hashlib
import os
from datetime import datetime, timezone

# Chunk size for reading files during hash calculation
# 8KB is a good balance between memory usage and I/O performance
CHUNK_SIZE = 8192


def calculate_file_hash(file_path: str, algorithm: str = "md5") -> str:
    """
    Calculate hash of a file efficiently using chunks.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use ("md5" or "sha256")
    
    Returns:
        Hexadecimal hash string
    """
    hash_func = hashlib.md5() if algorithm == "md5" else hashlib.sha256()
    
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()


def get_file_metadata(file_path: str) -> dict:
    """
    Get file metadata including hash, size, and modification time.
    
    Args:
        file_path: Path to the file
    
    Returns:
        Dictionary with file metadata
    """
    if not os.path.exists(file_path):
        return None
    
    stat_info = os.stat(file_path)
    file_hash = calculate_file_hash(file_path)
    
    modified_at = datetime.fromtimestamp(stat_info.st_mtime, tz=timezone.utc)
    
    return {
        "hash": file_hash,
        "size": stat_info.st_size,
        "modified_at": modified_at.isoformat(),
        "exists": True
    }
