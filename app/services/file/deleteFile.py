from fastapi import HTTPException
from app.models.user import User
import os
from app.core.config import config


def DeleteFile(file_path: str, user: User):
    """
    Deletes a file at the specified path.
    :param file_path: The path of the file to delete.
    :param user: The user requesting the deletion.
    """
    base_path = os.path.join(config.DIR_LOCATION, "data", user.root_foldername)
    path_to_delete = os.path.join(base_path, file_path)
    
    # Security check: ensure file is within user's directory
    path_to_delete = os.path.normpath(path_to_delete)
    base_path = os.path.normpath(base_path)
    if not path_to_delete.startswith(base_path):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not os.path.exists(path_to_delete):
        raise FileNotFoundError(f"File not found: {file_path}")

    if not os.access(path_to_delete, os.W_OK):
        raise PermissionError(f"Permission denied: {file_path}")

    os.remove(path_to_delete)
