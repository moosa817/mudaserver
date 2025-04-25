from fastapi import UploadFile, HTTPException
from pathlib import Path
from PIL import Image
import os
import uuid
from app.core.config import config


async def save_file(file: UploadFile) -> str:
    """
    Save the uploaded image file to a specific directory, resize it to 128x128 pixels,
    and return the file's location (path).
    """
    # Define the upload directory
    upload_dir = Path(config.DIR_LOCATION) / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Ensure the file is a valid image type
    valid_extensions = ["image/png", "image/webp", "image/jpeg"]
    if file.content_type not in valid_extensions:
        raise HTTPException(
            status_code=415,
            detail="Unsupported file type. Please upload a PNG, WebP, or JPEG image.",
        )

    # Generate a unique filename
    original_filename = file.filename
    file_extension = Path(original_filename).suffix.lower()
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    file_location = upload_dir / unique_filename

    try:
        # Save the file to disk
        with open(file_location, "wb") as f:
            content = await file.read()
            f.write(content)

        # Open the image and resize it to 128x128
        with Image.open(file_location) as img:
            img = img.resize((128, 128), Image.LANCZOS)
            img.save(file_location)  # Overwrite the file with the resized image

    except Exception as e:
        # If any error occurs, delete the partially uploaded file and raise HTTP exception
        if file_location.exists():
            os.remove(file_location)
        raise HTTPException(
            status_code=500, detail=f"Error processing the image: {str(e)}"
        )

    # Return the file's location
    return str(file_location)
