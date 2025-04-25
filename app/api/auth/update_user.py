from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.models.user import User
from app.schemas.auth.input.update_user import UpdateUserRequest
from app.api.auth.dependencies import get_current_user
from app.services.auth.fileupload import save_file

updateroute = APIRouter()


@updateroute.put("/update")
async def update(
    username: str = Form(...),
    email: str = Form(...),
    pfp: UploadFile | None = File(None),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    try:
        UpdateUserRequest(
            username=username,
            email=email,
        )
    except ValidationError as e:
        first_error = e.errors()[0]
        field = first_error.get("loc", ["?"])[-1]
        message = first_error.get("msg", "Invalid input")

        raise HTTPException(
            status_code=422,
            detail=jsonable_encoder(
                {
                    "success": False,
                    "field": field,
                    "message": message,
                }
            ),
        )

    db_user = db.query(User).filter(User.id == user["sub"]).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if email and db_user.email != email:
        if db.query(User).filter(User.email == email).first():
            raise HTTPException(status_code=400, detail="Email already in use")
        db_user.email = email
    if username and db_user.username != username:
        if db.query(User).filter(User.username == username).first():
            raise HTTPException(status_code=400, detail="Username already in use")
        db_user.username = username

    if pfp:
        # Assuming you have a function to save the file and get the URL
        pfp_url = await save_file(pfp)
        db_user.pfp = pfp_url

    db.commit()
    db.refresh(db_user)

    return {
        "message": "User updated successfully",
        "user": {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "pfp": db_user.pfp,
        },
    }
