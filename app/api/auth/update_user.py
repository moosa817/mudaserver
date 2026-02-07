from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.models.user import User
from app.api.dependencies import get_current_user
from app.services.auth.fileupload import save_file
from fastapi.responses import JSONResponse
import re
import logging

logger = logging.getLogger(__name__)
updateroute = APIRouter()


def validate_email_format(email: str) -> bool:
    regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(regex, email))


def validate_username_format(username: str) -> bool:
    # Add your username validation logic here
    # For example, check if it contains only alphanumeric characters and is between 3-20 characters long
    return 3 <= len(username) <= 20 and username.isalnum()


@updateroute.put("/update")
async def update(
    username: str | None = Form(None),
    email: str | None = Form(None),
    pfp: UploadFile | None = File(None),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if email and user.email != email:
            if db.query(User).filter(User.email == email).first():
                raise HTTPException(status_code=400, detail="Email already in use")

            # validate email format
            if not validate_email_format(email):
                raise HTTPException(status_code=400, detail="Invalid email format")
            user.email = email
        if username and user.username != username:
            if db.query(User).filter(User.username == username).first():
                raise HTTPException(status_code=400, detail="Username already in use")

            if not validate_username_format(username):
                raise HTTPException(status_code=400, detail="Invalid username format")

            user.username = username

        if pfp:
            # Assuming you have a function to save the file and get the URL
            pfp_url = await save_file(pfp)
            user.pfp = pfp_url

        db.add(user)
        db.commit()
        db.refresh(user)

        return JSONResponse(
            status_code=200,
            content={
                "message": "User updated successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "pfp": user.pfp,
                },
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during user update: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An error occurred during user update. Please try again.",
        )
