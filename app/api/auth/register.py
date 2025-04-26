from fastapi import APIRouter, Depends, HTTPException
from app.api.dependencies import get_db
from app.models.user import User
from app.schemas.auth.input.register import RegisterInput
from app.services.folder.createfolder import create_root_folder
from app.schemas.auth.ouput.register import RegisterResponse
from sqlalchemy.orm import Session
import time
from app.services.auth.security import (
    create_jwt_token,
    create_refresh_token,
    hash_password,
)

registerroute = APIRouter()


@registerroute.post("/register", response_model=RegisterResponse)
async def register(user_input: RegisterInput, db: Session = Depends(get_db)):

    # 🔹 Check if username exists
    if db.query(User).filter(User.username == user_input.username).first():
        raise HTTPException(status_code=409, detail="Username is already taken.")

    # 🔹 Check if email exists
    if db.query(User).filter(User.email == user_input.email).first():
        raise HTTPException(status_code=409, detail="Email is already registered.")

    # 🔹 Hash password
    hashed_password = hash_password(user_input.password)

    # 🔹 Create user
    new_user = User(
        username=user_input.username,
        email=user_input.email,
        hashed_password=hashed_password,
    )

    safe_username = "".join(
        c for c in user_input.username if c.isalnum() or c in ("-", "_")
    ).lower()
    foldername = safe_username + f"_{int(time.time())}"

    # 🔹 Create root folder for user
    if not create_root_folder(foldername):
        raise HTTPException(
            status_code=500,
            detail="Failed to create root folder for user.",
        )

    new_user.foldername = foldername
    new_user.storage_size = 0

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_jwt_token(
        {
            "sub": new_user.username,
            "token_type": "access",
        }
    )
    refresh_token = create_refresh_token(
        {
            "sub": new_user.username,
            "token_type": "refresh",
        }
    )
    id = new_user.id
    username = new_user.username
    email = new_user.email

    return RegisterResponse(
        id=id,
        username=username,
        email=email,
        pfp="",
        access_token=access_token,
        refresh_token=refresh_token,
    )
