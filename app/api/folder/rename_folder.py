from fastapi import APIRouter, Depends, HTTPException
from app.api.dependencies import get_current_user
from app.models.user import User
from app.core.config import config
from app.services.folder.createfolder import validFolderName
import os


renameroute = APIRouter()


@renameroute.put("/rename_folder")
async def rename_folder(
    old_name: str, new_name: str, user: User = Depends(get_current_user)
):
    """
    Rename a folder from old_name to new_name.
    """
    if not validFolderName(new_name):
        raise HTTPException(
            status_code=400,
            detail="Folder name can only contain letters, numbers, and underscores. and be under 255 characters.",
        )

    # Check if the folder exists
    old_folder_path = os.path.join(
        f"{config.DIR_LOCATION}/data", user.foldername, old_name
    )
    if not os.path.exists(old_folder_path):
        raise HTTPException(
            status_code=404,
            detail="Folder does not exist.",
        )
    # Check if the new folder name already exists
    new_folder_path = os.path.join(
        f"{config.DIR_LOCATION}/data", user.foldername, new_name
    )
    if os.path.exists(new_folder_path):
        raise HTTPException(
            status_code=409,
            detail="Folder with the new name already exists.",
        )
    # Rename the folder
    try:
        os.rename(old_folder_path, new_folder_path)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error renaming folder: {str(e)}",
        )
    return {"message": "Folder renamed successfully."}
