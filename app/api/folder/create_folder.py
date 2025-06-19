from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.core.config import config
from app.services.folder.createfolder import create_folder as CreateFolder
from app.services.folder.validations import validFolderName


createroute = APIRouter()


# if root path is empty just create a folder in the root directory
@createroute.post("/create_folder")
async def create_folder(
    folder_name: str,
    root_path: str = "root",  # optional, defaults to "root"
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    folder_name = folder_name.lower()
    # valid folder name
    if not validFolderName(folder_name):
        raise HTTPException(
            status_code=400,
            detail="Folder name can only contain letters, numbers, and underscores. and be under 255 characters.",
        )

    CreateFolder(
        user.root_foldername,
        folder_name,
        root_path,
    )
    user.storage_used += 4096
    db.add(user)
    db.commit()

    return {"message": "Folder created successfully."}
