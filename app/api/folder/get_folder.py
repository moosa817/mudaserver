from fastapi import APIRouter, HTTPException, Depends
from app.api.dependencies import get_current_user
from app.services.folder.getfolder import getfolder
from app.models.user import User

getfolderroute = APIRouter()


@getfolderroute.get("/get_folder")
async def get_folder(folder_name: str, user: User = Depends(get_current_user)):
    """
    Get a folder with the given name.
    """
    folder = getfolder(user.foldername, folder_name)
    if "error" in folder:
        raise HTTPException(status_code=404, detail=folder["error"])
    return folder
