from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from app.api.dependencies import get_current_user
from app.models.user import User
from app.core.config import config
import os
import aiofiles
import logging

logger = logging.getLogger(__name__)
view_router = APIRouter()


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

        # Stream video/audio files
        if ext in [".mp4", ".mp3", ".wav", ".ogg", ".webm"]:
            from fastapi.responses import StreamingResponse

            def iterfile():
                with open(file_path, "rb") as f:
                    yield from f

            return StreamingResponse(
                iterfile(), media_type=f"video/mp4" if ext == ".mp4" else f"audio/{ext[1:]}"
            )

        # Direct display for images, pdf, etc.
        return FileResponse(file_path)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error viewing file: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while viewing the file.",
        )
