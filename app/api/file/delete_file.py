from fastapi import APIRouter, HTTPException, Depends
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.file.deleteFile import DeleteFile

delete_file_router = APIRouter()


@delete_file_router.delete("/delete_file")
async def delete_file(file_path: str, user: User = Depends(get_current_user)):
    """
    Delete a file at the specified path.
    :param file_path: The path of the file to delete.
    """
    file_path = file_path.strip().lower()

    if not file_path:
        raise HTTPException(status_code=400, detail="Invalid file path")

    try:
        DeleteFile(file_path, user)
    except:
        raise HTTPException(status_code=500, detail="Failed to delete file")

    return {"success": True, "message": "File deleted successfully"}
