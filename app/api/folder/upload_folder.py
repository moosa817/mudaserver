from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
import os
from app.core.config import config
from app.api.dependencies import get_current_user, get_db
from app.models.user import User

uploadroute = APIRouter()


@uploadroute.post("/upload_folder")
async def upload_folder(
    files: list[UploadFile] = File(...),
    root_path: str = Form("root"),  # default to "root"
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Uploads an entire folder (with subfolders) to the specified root_path.
    If root_path="root" → uploads to user.root_foldername/root
    If root_path="root/somefolder" → uploads inside that subfolder.
    """

    if root_path == "root":
        root_path = ""

    base_dir = os.path.join(
        config.DIR_LOCATION, "data", user.root_foldername, root_path
    )

    uploaded_size = 0

    for file in files:
        relative_path = file.filename  # contains subfolder path (webkitRelativePath)
        save_path = os.path.join(base_dir, relative_path)

        # create parent dirs
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        contents = await file.read()
        uploaded_size += len(contents)

        with open(save_path, "wb") as buffer:
            buffer.write(contents)

    # update storage usage
    user.storage_used += uploaded_size
    db.add(user)
    db.commit()

    return {
        "message": "Folder uploaded successfully.",
        "root_path": root_path,
        "files_uploaded": len(files),
        "size_uploaded": uploaded_size,
    }
