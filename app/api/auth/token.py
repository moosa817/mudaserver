from fastapi import APIRouter, Depends, HTTPException, Response
from app.services.auth.security import (
    create_jwt_token,
    verify_password,
    create_refresh_token,
)
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.auth.ouput.login import TokenResponse
from app.core.config import config
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.models.user import User


tokenroute = APIRouter()


@tokenroute.post("/token", response_model=TokenResponse)
async def login(
    request: OAuth2PasswordRequestForm = Depends(),
    response: Response = None,
    db: Session = Depends(get_db),
):
    """Authenticate user and return both access and refresh tokens."""
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=403, detail="Invalid credentials")

    access_token = create_jwt_token(
        {
            "sub": f"{user.id}",
            "token_type": "access",
        }
    )
    refresh_token = create_refresh_token(
        {
            "sub": f"{user.id}",
            "token_type": "refresh",
        }
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
    )
