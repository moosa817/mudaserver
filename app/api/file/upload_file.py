from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.device import Device
from app.core.config import config
from app.services.upload.progress_tracker import progress_tracker  # ✅ Add this
import os
import aiofiles
from typing import Optional

upload_router = APIRouter()


@upload_router.post("/upload-chunk")
async def upload_chunk(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    file_id: str = Form(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
    file: UploadFile = File(...),
    folder_path: str = Form("root"),
    device_id: Optional[str] = Form(None),
):
    folder_path = folder_path.strip().lower()
    base_dir = os.path.join(config.DIR_LOCATION, "data", user.root_foldername)
    
    # If device_id is provided, scope to device folder
    if device_id:
        device = db.query(Device).filter(
            Device.device_id == device_id,
            Device.user_id == user.id
        ).first()
        
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        base_dir = os.path.join(base_dir, device.folder_name)
    
    if folder_path != "root":
        base_dir = os.path.join(base_dir, folder_path)
    os.makedirs(base_dir, exist_ok=True)

    temp_dir = os.path.join(base_dir, f"{file_id}_parts")
    os.makedirs(temp_dir, exist_ok=True)

    chunk_path = os.path.join(temp_dir, f"part_{chunk_index}")
    async with aiofiles.open(chunk_path, "wb") as f:
        while True:
            chunk = await file.read(1024 * 1024)  # 1 MB at a time
            if not chunk:
                break
            await f.write(chunk)

    # ✅ Update progress after each chunk
    progress_tracker.set_progress(
        upload_id=file_id,
        current=chunk_index + 1,
        total=total_chunks,
        filename=file.filename,
    )

    # merge if all chunks uploaded
    uploaded_parts = len([p for p in os.listdir(temp_dir) if p.startswith("part_")])
    if uploaded_parts == total_chunks:
        final_path = os.path.join(base_dir, file.filename)
        with open(final_path, "wb") as outfile:
            for i in range(total_chunks):
                part_path = os.path.join(temp_dir, f"part_{i}")
                with open(part_path, "rb") as infile:
                    outfile.write(infile.read())

        # clean up parts
        for p in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, p))
        os.rmdir(temp_dir)

        # ✅ Remove progress when complete
        progress_tracker.remove_progress(file_id)

        return JSONResponse(
            content={
                "success": True,
                "file_location": final_path,
                "message": "Upload complete",
            }
        )

    return JSONResponse(
        content={
            "success": True,
            "message": f"Chunk {chunk_index + 1}/{total_chunks} uploaded",
        }
    )


# ✅ Add endpoint to check upload progress
@upload_router.get("/upload-progress/{file_id}")
async def get_upload_progress(file_id: str, user: User = Depends(get_current_user)):
    """
    Get the current progress of a file upload.
    """
    progress = progress_tracker.get_progress(file_id)

    if not progress:
        raise HTTPException(status_code=404, detail="Upload not found")

    return {
        "file_id": file_id,
        "current_chunk": progress.get("current", 0),
        "total_chunks": progress.get("total", 0),
        "percentage": round(progress.get("percentage", 0), 2),
        "filename": progress.get("filename", ""),
    }
