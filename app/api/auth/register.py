from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from app.api.dependencies import get_db
from app.models.user import User
from app.schemas.auth.input.register import RegisterInput

from app.schemas.auth.ouput.register import RegisterResponse
from sqlalchemy.orm import Session
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
        raise HTTPException(status_code=400, detail="Username is already taken.")

    # 🔹 Check if email exists
    if db.query(User).filter(User.email == user_input.email).first():
        raise HTTPException(status_code=400, detail="Email is already registered.")

    # 🔹 Hash password
    hashed_password = hash_password(user_input.password)

    # 🔹 Create user
    new_user = User(
        username=user_input.username,
        email=user_input.email,
        hashed_password=hashed_password,
    )
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
    pfp = new_user.pfp

    return RegisterResponse(
        id=id,
        username=username,
        email=email,
        pfp="",
        access_token=access_token,
        refresh_token=refresh_token,
    )
