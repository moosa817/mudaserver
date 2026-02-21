import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from app.api.dependencies import verify_basic_auth
from app.core.config import config

mediarouter = APIRouter()

# Define common extensions
VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".webm"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".gif"}


@mediarouter.get("/list_media")
async def list_media(username: str = Depends(verify_basic_auth)):
    media_list = []

    if not os.path.exists(config.THUMBS_PATH):
        raise HTTPException(status_code=500, detail="Minified directory not found")

    # We walk the original media to find the actual extensions
    for root, _, files in os.walk(config.MEDIA_PATH):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in IMAGE_EXTS or ext in VIDEO_EXTS:

                # Path relative to ALL folder
                rel_path = os.path.relpath(os.path.join(root, file), config.MEDIA_PATH)

                # Construct the expected thumbnail path (everything in minified is .jpg)
                thumb_rel_path = os.path.splitext(rel_path)[0] + ".jpg"
                thumb_full_path = os.path.join(config.THUMBS_PATH, thumb_rel_path)

                # Only include if the thumbnail actually exists
                if os.path.exists(thumb_full_path):
                    media_list.append(
                        {
                            "type": "video" if ext in VIDEO_EXTS else "image",
                            "full_path": rel_path,
                            "thumb_path": thumb_rel_path,
                            "filename": file,
                        }
                    )

    # Sort by filename or path (usually contains dates like 2017/...)
    return {"media": sorted(media_list, key=lambda x: x["full_path"], reverse=True)}


@mediarouter.get("/thumb/{file_path:path}")
async def get_thumbnail(file_path: str, username: str = Depends(verify_basic_auth)):
    full_path = os.path.join(config.THUMBS_PATH, file_path)
    if not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    return FileResponse(full_path)


@mediarouter.get("/full/{file_path:path}")
async def get_full_res(file_path: str, username: str = Depends(verify_basic_auth)):
    full_path = os.path.join(config.MEDIA_PATH, file_path)

    # Security check
    if not os.path.abspath(full_path).startswith(os.path.abspath(config.MEDIA_PATH)):
        raise HTTPException(status_code=403, detail="Access denied")

    if not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="Original file not found")

    return FileResponse(full_path)
