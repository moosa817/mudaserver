from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from app.api.dependencies import get_current_user
from app.models.user import User
from app.core.config import config
import os
import zipfile
import tempfile
import shutil
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

download_folder_router = APIRouter()


def cleanup_temp_file(file_path: str):
    """
    Background task to delete temporary zip file after download completes.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up temporary file: {file_path}")
    except Exception as e:
        logger.error(f"Failed to cleanup temp file {file_path}: {e}")


def create_zip_archive(source_dir: str, output_path: str) -> int:
    """
    Create a zip archive of a directory.
    Returns the size of the zip file in bytes.
    """
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Walk through the directory
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Calculate relative path for zip archive
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)

    return os.path.getsize(output_path)


@download_folder_router.get("/download/{path:path}")
async def download_folder(
    path: str, background_tasks: BackgroundTasks, user: User = Depends(get_current_user)
):
    """
    Download an entire folder as a ZIP archive.
    The folder will be compressed on-the-fly and sent to the client.
    The temporary zip file is automatically cleaned up after download.
    """
    path = path.strip()  # Only strip whitespace, preserve case

    # Handle root folder
    if not path or path == "root":
        path = ""

    # Construct full folder path
    base_path = os.path.join(config.DIR_LOCATION, "data", user.root_foldername)
    folder_path = os.path.join(base_path, path) if path else base_path

    # Security check: ensure folder is within user's directory
    folder_path = os.path.normpath(folder_path)
    base_path = os.path.normpath(base_path)
    if not folder_path.startswith(base_path):
        raise HTTPException(status_code=403, detail="Access denied")

    # Check if folder exists
    if not os.path.exists(folder_path):
        raise HTTPException(status_code=404, detail="Folder not found")

    # Check if it's a directory
    if not os.path.isdir(folder_path):
        raise HTTPException(status_code=400, detail="Path is not a folder")

    # Check if folder is empty
    if not os.listdir(folder_path):
        raise HTTPException(status_code=400, detail="Folder is empty")

    try:
        # Create temporary file for zip
        temp_dir = tempfile.gettempdir()
        folder_name = (
            os.path.basename(folder_path) if path else f"{user.username}_drive"
        )
        zip_filename = f"{folder_name}.zip"
        temp_zip_path = os.path.join(
            temp_dir, f"{user.username}_{folder_name}_{os.getpid()}.zip"
        )

        # Create zip archive
        logger.info(f"Creating zip archive: {temp_zip_path}")
        zip_size = create_zip_archive(folder_path, temp_zip_path)
        logger.info(f"Zip archive created: {zip_size} bytes")

        # Schedule cleanup after response is sent
        background_tasks.add_task(cleanup_temp_file, temp_zip_path)

        # Return zip file
        return FileResponse(
            path=temp_zip_path,
            media_type="application/zip",
            filename=zip_filename,
            headers={
                "Content-Disposition": f'attachment; filename="{zip_filename}"',
                "Content-Length": str(zip_size),
            },
        )

    except Exception as e:
        logger.error(f"Failed to create zip archive: {e}")
        # Clean up if zip was partially created
        if os.path.exists(temp_zip_path):
            try:
                os.remove(temp_zip_path)
            except:
                pass
        raise HTTPException(
            status_code=500, detail=f"Failed to create archive: {str(e)}"
        )
