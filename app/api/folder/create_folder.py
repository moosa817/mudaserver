from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.core.config import config
from app.services.folder.createfolder import create_folder as CreateFolder
from app.services.folder.createfolder import validFolderName
import re


createroute = APIRouter()


@createroute.post("/create_folder")
async def create_folder(
    folder_name: str,
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

    if not CreateFolder(
        user.foldername,
        folder_name,
    ):
        raise HTTPException(
            status_code=409,
            detail="Folder already exists.",
        )
    user.storage_size += 4096
    db.add(user)
    db.commit()

    return {"message": "Folder created successfully."}
