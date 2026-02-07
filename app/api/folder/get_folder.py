from fastapi import APIRouter, HTTPException, Depends
from app.api.dependencies import get_current_user
from app.models.user import User
from app.core.config import config
import os
from datetime import datetime, timezone

getfolderroute = APIRouter()


@getfolderroute.get("/get_folder")
async def get_folder(folder_path: str = "", user: User = Depends(get_current_user)):
    """
    Get a folder with the given name.
    Returns list of items with metadata (name, type, size, modified).
    """
    folder_path = folder_path.strip()  # Only strip whitespace, preserve case
    
    if folder_path == "root" or not folder_path:
        folder_path = ""
    
    base_path = os.path.join(config.DIR_LOCATION, "data", user.root_foldername)
    full_path = os.path.join(base_path, folder_path) if folder_path else base_path
    
    # Security check: ensure path is within user's directory
    full_path = os.path.realpath(full_path)
    base_path = os.path.realpath(base_path)
    if not full_path.startswith(base_path + os.sep) and full_path != base_path:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Folder not found")
    
    if not os.path.isdir(full_path):
        raise HTTPException(status_code=400, detail="Path is not a folder")
    
    items = []
    # Use os.scandir() for better performance
    with os.scandir(full_path) as entries:
        for entry in entries:
            # Skip symbolic links for security
            if entry.is_symlink():
                continue
                
            is_file = entry.is_file(follow_symlinks=False)
            
            item_data = {
                "name": entry.name,
                "type": "file" if is_file else "folder",
            }
            
            # Add file metadata
            if is_file:
                stat = entry.stat(follow_symlinks=False)
                item_data["size"] = stat.st_size  # File size in bytes
                item_data["modified"] = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
            
            items.append(item_data)
    
    return {"items": items}
