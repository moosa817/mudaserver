from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from app.api.dependencies import get_current_user
from app.models.user import User
from app.core.config import config
import os
import logging

logger = logging.getLogger(__name__)
view_router = APIRouter()

# Dictionary mapping file extensions to proper MIME types for viewable files
VIEWABLE_TYPES = {
    # Images
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
    # Documents
    ".pdf": "application/pdf",
    # Text
    ".txt": "text/plain",
    ".json": "application/json",
    ".md": "text/markdown",
    # Video
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".mov": "video/quicktime",
    # Audio
    ".mp3": "audio/mpeg",  # RFC-compliant MIME type (not "audio/mp3")
    ".wav": "audio/wav",
    ".ogg": "audio/ogg",
}


@view_router.get("/view/{path:path}")
async def view_file(path: str, user: User = Depends(get_current_user)):
    try:
        path = path.strip()
        
        if not path:
            raise HTTPException(status_code=400, detail="File path is required")
        
        base_path = os.path.join(config.DIR_LOCATION, "data", user.root_foldername)
        file_path = os.path.join(base_path, path)

        # Security check: ensure file is within user's directory
        file_path = os.path.realpath(file_path)
        base_path = os.path.realpath(base_path)
        try:
            if os.path.commonpath([file_path, base_path]) != base_path:
                raise HTTPException(status_code=403, detail="Access denied")
        except ValueError:
            # Different drives on Windows or other path issues
            raise HTTPException(status_code=403, detail="Access denied")

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        if not os.path.isfile(file_path):
            raise HTTPException(status_code=400, detail="Path is not a file")

        ext = os.path.splitext(file_path)[1].lower()

        # Validate that file type is viewable
        if ext not in VIEWABLE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"File type '{ext}' is not supported for inline viewing."
            )

        # Get the proper media type for the file
        media_type = VIEWABLE_TYPES[ext]
        
        # Get filename for Content-Disposition header and sanitize it
        filename = os.path.basename(file_path)
        # Sanitize filename by removing/escaping characters that could break HTTP headers
        # Replace quotes and backslashes with underscores to prevent header injection
        safe_filename = filename.replace('"', '_').replace('\\', '_').replace('\n', '_').replace('\r', '_')

        # Return file with inline disposition header for browser viewing
        return FileResponse(
            path=file_path,
            media_type=media_type,
            headers={"Content-Disposition": f'inline; filename="{safe_filename}"'}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error viewing file: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while viewing the file.",
        )
