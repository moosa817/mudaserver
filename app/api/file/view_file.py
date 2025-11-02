from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from app.api.dependencies import get_current_user
from app.models.user import User
from app.core.config import config
import os
import aiofiles

view_router = APIRouter()


@view_router.get("/view/{path:path}")
async def view_file(path: str, user: User = Depends(get_current_user)):
    base_path = os.path.join(config.DIR_LOCATION, "data", user.root_foldername)
    file_path = os.path.join(base_path, path)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

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
