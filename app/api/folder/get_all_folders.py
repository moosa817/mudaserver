from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.folder.getfolder import getallfolders


getallfoldersroute = APIRouter()


@getallfoldersroute.get("/get_all_folders")
async def get_all_folders(user: User = Depends(get_current_user)):
    """
    Get all folders.
    """
    folders = getallfolders(user.foldername)
    return folders
