from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from fastapi.responses import JSONResponse
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.file.uploadfile import UploadMyFile
from app.core.config import config
import os

upload_router = APIRouter()


@upload_router.post("/upload")
async def upload_file(
    user: User = Depends(get_current_user),
    file: UploadFile = File(),
    folder_path: str = Form("root"),
):
    """
    Upload a file to the server.
    """
    folder_path = folder_path.strip().lower()
    if not folder_path == "root":
        folder_location = os.path.join(
            f"{config.DIR_LOCATION}/data", user.root_foldername, folder_path
        )
    else:
        folder_location = os.path.join(
            f"{config.DIR_LOCATION}/data", user.root_foldername
        )

    file_location = UploadMyFile(file, folder_location)
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "file_location": file_location,
            "message": "File uploaded successfully",
        },
    )
