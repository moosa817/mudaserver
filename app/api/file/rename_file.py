from fastapi import APIRouter, Depends, HTTPException
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.file.renameFile import RenameMyFile
from fastapi.responses import JSONResponse
from app.services.file.validFile import is_valid_file_name

rename_router = APIRouter()


@rename_router.put("/rename")
async def rename_file(
    old_file_path: str,
    new_file_name: str,
    user: User = Depends(get_current_user),
):
    """
    Rename a file on the server.
    """
    old_file_path = old_file_path.strip().lower()
    new_file_name = new_file_name.strip().lower()

    if not is_valid_file_name(new_file_name):
        raise HTTPException(
            status_code=400,
            detail="File name can only contain letters, numbers, underscores, and dashes, and must be under 255 characters.",
        )

    if not old_file_path or not new_file_name:
        raise HTTPException(status_code=400, detail="Invalid file path or new name")

    try:
        new_file_location = RenameMyFile(old_file_path, new_file_name, user)
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "new_file_location": new_file_location,
                "message": "File renamed successfully",
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
