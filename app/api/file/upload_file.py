from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from app.api.dependencies import get_current_user
from app.models.user import User
from app.core.config import config
import os
import aiofiles

upload_router = APIRouter()


@upload_router.post("/upload-chunk")
async def upload_chunk(
    user: User = Depends(get_current_user),
    file_id: str = Form(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
    file: UploadFile = File(...),
    folder_path: str = Form("root"),
):
    folder_path = folder_path.strip().lower()
    base_dir = os.path.join(config.DIR_LOCATION, "data", user.root_foldername)
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
