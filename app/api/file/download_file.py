from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from app.api.dependencies import get_current_user
from app.models.user import User
from app.core.config import config
import os
import mimetypes

download_file_router = APIRouter()


@download_file_router.get("/download/{path:path}")
async def download_file(path: str, user: User = Depends(get_current_user)):
    """
    Download a specific file from the server.
    Returns the file with proper headers to trigger browser download.
    """
    path = path.strip()  # Only strip whitespace, preserve case

    if not path:
        raise HTTPException(status_code=400, detail="File path is required")

    # Construct full file path
    base_path = os.path.join(config.DIR_LOCATION, "data", user.root_foldername)
    file_path = os.path.join(base_path, path)

    # Security check: ensure file is within user's directory
    file_path = os.path.realpath(file_path)
    base_path = os.path.realpath(base_path)
    if not file_path.startswith(base_path + os.sep) and file_path != base_path:
        raise HTTPException(status_code=403, detail="Access denied")

    # Check if file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Check if it's a file (not a directory)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=400, detail="Path is not a file")

    # Get the correct MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = "application/octet-stream"

    # Get just the filename (not the full path)
    filename = os.path.basename(file_path)

    # Return file with download headers
    return FileResponse(
        path=file_path,
        media_type=mime_type,
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
