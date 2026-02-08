from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from app.api.dependencies import get_current_user
from app.models.user import User
from app.core.config import config
import os
import logging
from urllib.parse import quote

logger = logging.getLogger(__name__)
view_router = APIRouter()

# Maximum file size for inline viewing (30MB)
MAX_VIEW_SIZE = 30 * 1024 * 1024  # 30MB in bytes

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

        # Check file size (30MB limit for inline viewing)
        file_size = os.path.getsize(file_path)

        if file_size > MAX_VIEW_SIZE:
            filename = os.path.basename(file_path)
            download_url = f"/api/file/download/{quote(path)}"
            
            raise HTTPException(
                status_code=413,  # Payload Too Large
                detail={
                    "error": "file_too_large",
                    "message": f"File is too large for inline viewing ({file_size / (1024*1024):.2f} MB). Please download instead.",
                    "file_size": file_size,
                    "size_limit": MAX_VIEW_SIZE,
                    "download_url": download_url,
                    "filename": filename
                }
            )

        ext = os.path.splitext(file_path)[1].lower()

        # Validate that file type is viewable
        if ext not in VIEWABLE_TYPES:
            filename = os.path.basename(file_path)
            download_url = f"/api/file/download/{quote(path)}"
            
            raise HTTPException(
                status_code=415,  # Unsupported Media Type
                detail={
                    "error": "unsupported_file_type",
                    "message": f"File type '{ext}' cannot be viewed in browser. Please download instead.",
                    "file_extension": ext,
                    "download_url": download_url,
                    "filename": filename
                }
            )

        # Get the proper media type for the file
        media_type = VIEWABLE_TYPES[ext]

        # Get filename for Content-Disposition header
        filename = os.path.basename(file_path)

        # Sanitize and encode filename for Content-Disposition header
        # Use ASCII fallback for filename and RFC 5987 encoding for filename*
        # This ensures proper handling of Unicode characters across all browsers
        ascii_filename = filename.encode('ascii', 'ignore').decode('ascii')
        if not ascii_filename:
            # If filename is entirely non-ASCII, use 'file' + original extension
            # ext is already validated to be in VIEWABLE_TYPES, so it's safe
            ascii_filename = f'file{ext}'
        # Escape special characters to prevent header injection (quotes, backslashes, CRLF)
        ascii_filename = (ascii_filename
                         .replace('\\', '\\\\')
                         .replace('"', '\\"')
                         .replace('\r', '')
                         .replace('\n', ''))
        encoded_filename = quote(filename, safe='')

        # Use both filename (ASCII fallback) and filename* (UTF-8 encoded) for maximum compatibility
        # RFC 5987 format: filename*=UTF-8'<language>'{encoded_name} (language tag is optional/empty here)
        content_disposition = f'inline; filename="{ascii_filename}"; filename*=UTF-8\'\'{encoded_filename}'

        # Return file with inline disposition header for browser viewing
        return FileResponse(
            path=file_path,
            media_type=media_type,
            headers={"Content-Disposition": content_disposition}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error viewing file: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while viewing the file.",
        )
