from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.services.folder.deletefolder import DeleteFolder

deleteroute = APIRouter()


@deleteroute.delete("/delete_folder")
async def delete_folder(
    folder_name: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a folder with the given name.
    """
    rootfolder = user.foldername
    if not DeleteFolder(rootfolder, folder_name):
        raise HTTPException(
            status_code=404,
            detail="Folder not found.",
        )
    user.storage_size -= 4096
    db.add(user)
    db.commit()
    return {"message": "Folder deleted successfully."}
