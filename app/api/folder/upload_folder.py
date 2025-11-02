from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import aiofiles
import uuid  # ✅ Add this
from app.core.config import config
from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.services.upload.progress_tracker import progress_tracker  # ✅ Add this

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

    # ✅ Generate upload ID for progress tracking
    upload_id = str(uuid.uuid4())
    total_files = len(files)

    if root_path == "root":
        root_path = ""

    base_dir = os.path.join(
        config.DIR_LOCATION, "data", user.root_foldername, root_path
    )
    os.makedirs(base_dir, exist_ok=True)

    uploaded_size = 0

    for idx, file in enumerate(files):
        relative_path = file.filename
        save_path = os.path.join(base_dir, relative_path)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # ✅ Update progress before processing each file
        progress_tracker.set_progress(
            upload_id=upload_id, current=idx, total=total_files, filename=file.filename
        )

        # Stream write to disk
        async with aiofiles.open(save_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):  # 1 MB at a time
                uploaded_size += len(chunk)
                await buffer.write(chunk)

    # Update user storage usage in DB
    user.storage_used += uploaded_size
    db.add(user)
    db.commit()

    # ✅ Remove progress when complete
    progress_tracker.remove_progress(upload_id)

    return {
        "message": "Folder uploaded successfully.",
        "upload_id": upload_id,  # ✅ Return upload ID
        "root_path": root_path,
        "files_uploaded": len(files),
        "size_uploaded": uploaded_size,
    }


# ✅ Add endpoint to check folder upload progress
@uploadroute.get("/upload-folder-progress/{upload_id}")
async def get_folder_upload_progress(
    upload_id: str, user: User = Depends(get_current_user)
):
    """
    Get the current progress of a folder upload.
    """
    progress = progress_tracker.get_progress(upload_id)

    if not progress:
        raise HTTPException(status_code=404, detail="Upload not found")

    return {
        "upload_id": upload_id,
        "current_file": progress.get("current", 0),
        "total_files": progress.get("total", 0),
        "percentage": round(progress.get("percentage", 0), 2),
        "current_filename": progress.get("filename", ""),
    }
