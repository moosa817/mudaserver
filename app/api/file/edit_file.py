from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_user
from app.models.user import User
from pydantic import BaseModel
import os
from app.core.config import config
from fastapi.exceptions import HTTPException
import logging

logger = logging.getLogger(__name__)


class EditFile(BaseModel):
    file_path: str
    content: str


class EditFileResponse(BaseModel):
    message: str


edit_router = APIRouter()


@edit_router.post("/edit-file", response_model=EditFileResponse)
async def edit_file(
    request: EditFile, user: User = Depends(get_current_user)
):  # edits text based file
    """
    Edit a text-based file.
    """
    try:
        # check if path exists and if it is of a text-based file
        if not request.file_path.endswith((".txt", ".md", ".json", ".csv")):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only text-based files are allowed.",
            )
        file_path = request.file_path.strip()
        content = request.content
        
        base_path = os.path.join(config.DIR_LOCATION, "data", user.root_foldername)
        full_path = os.path.join(base_path, file_path)

        # Security check: ensure file is within user's directory
        full_path = os.path.realpath(full_path)
        base_path = os.path.realpath(base_path)
        try:
            if os.path.commonpath([full_path, base_path]) != base_path:
                raise HTTPException(status_code=403, detail="Access denied")
        except ValueError:
            # Different drives on Windows or other path issues
            raise HTTPException(status_code=403, detail="Access denied")

        if not os.path.exists(full_path):
            raise HTTPException(
                status_code=404,
                detail="File not found.",
            )
        
        if not os.path.isfile(full_path):
            raise HTTPException(
                status_code=400,
                detail="Path is not a file.",
            )

        with open(full_path, "w") as file:
            file.write(content)

        return {"message": "File edited successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error editing file: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to edit file.",
        )
