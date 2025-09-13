from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_user
from app.models.user import User
from pydantic import BaseModel
import os
from app.core.config import config
from fastapi.exceptions import HTTPException


class EditFile(BaseModel):
    file_path: str
    content: str


edit_router = APIRouter()


@edit_router.post("/edit-file", response_model=EditFile, tags=["file"])
async def edit_file(
    request: EditFile, user: User = Depends(get_current_user)
):  # edits text based file
    """
    Edit a text-based file.
    """
    # check if path exists and if it is of a text-based file
    if not request.file_path.endswith((".txt", ".md", ".json", ".csv")):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only text-based files are allowed.",
        )
    file_path = request.file_path
    content = request.content
    full_path = os.path.join(f"{config.DIR_LOCATION}/data", user.username, file_path)

    if not os.path.exists(full_path):
        raise HTTPException(
            status_code=404,
            detail="File not found.",
        )

    try:
        with open(full_path, "w") as file:
            file.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to edit file: {str(e)}",
        )

    return {"message": "File edited successfully", "file_path": file_path}
