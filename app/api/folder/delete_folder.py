from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.services.folder.deletefolder import DeleteFolder

deleteroute = APIRouter()


@deleteroute.delete("/delete_folder")
async def delete_folder(
    folder_path: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a folder with the given name.
    """
    folder_path = folder_path.lower().strip()

    if not folder_path:
        raise HTTPException(
            status_code=400,
            detail="Folder path cannot be empty.",
        )

    rootfolder = user.root_foldername
    if not DeleteFolder(rootfolder, folder_path):
        raise HTTPException(
            status_code=404,
            detail="Folder not found.",
        )

    db.add(user)
    db.commit()
    return {"message": "Folder deleted successfully."}
