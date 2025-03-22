from fastapi import APIRouter, HTTPException, Response
from app.services.auth.security import (
    create_jwt_token,
    verify_password,
    hash_password,
    create_refresh_token,
)
from app.schemas.auth.input.login import LoginRequest
from app.schemas.auth.ouput.login import TokenResponse
from app.core.config import config

tokenroute = APIRouter()

# Mock user database
fake_users_db = {
    "testuser": {"username": "testuser", "password": hash_password("testpassword")}
}


@tokenroute.post("/token", response_model=TokenResponse)
async def login(request: LoginRequest, response: Response):
    """Authenticate user and return both access and refresh tokens."""
    user = fake_users_db.get(request.username)

    if not user or not verify_password(request.password, user["password"]):
        raise HTTPException(status_code=403, detail="Invalid credentials")

    access_token = create_jwt_token(
        {
            "sub": request.username,
            "token_type": "access",
        }
    )
    refresh_token = create_refresh_token(
        {
            "sub": request.username,
            "token_type": "refresh",
        }
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,  # Include refresh token in response
        "token_type": "bearer",
    }
