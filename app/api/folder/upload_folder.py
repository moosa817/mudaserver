from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import aiofiles
from app.core.config import config
from app.api.dependencies import get_current_user, get_db
from app.models.user import User

uploadroute = APIRouter()


@uploadroute.post("/upload_folder")
async def upload_folder(
    files: list[UploadFile] = File(...),
    root_path: str = Form("root"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Uploads an entire folder (with subfolders) to the specified root_path.
    Streams each file to disk in chunks to avoid memory overload.
    """

    # Adjust root folder logic
    if root_path == "root":
        root_path = ""

    base_dir = os.path.join(
        config.DIR_LOCATION, "data", user.root_foldername, root_path
    )
    os.makedirs(base_dir, exist_ok=True)

    uploaded_size = 0

    for file in files:
        relative_path = file.filename  # includes subfolders (webkitRelativePath)
        save_path = os.path.join(base_dir, relative_path)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Stream write to disk
        async with aiofiles.open(save_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):  # 1 MB at a time
                uploaded_size += len(chunk)
                await buffer.write(chunk)

    # Update user storage usage in DB
    user.storage_used += uploaded_size
    db.add(user)
    db.commit()

    return {
        "message": "Folder uploaded successfully.",
        "root_path": root_path,
        "files_uploaded": len(files),
        "size_uploaded": uploaded_size,
    }
