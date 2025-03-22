from fastapi import APIRouter, HTTPException
from app.services.auth.security import (
    create_jwt_token,
    verify_password,
    hash_password,
    create_refresh_token,
    decode_jwt_token,
)
from app.schemas.auth.input.refresh import RefreshTokenRequest
from app.schemas.auth.ouput.refresh import RefreshTokenResponse

refreshroute = APIRouter()


@refreshroute.post("/refresh", response_model=RefreshTokenResponse)
def refresh(request: RefreshTokenRequest):
    """Refresh access token using refresh token."""
    payload = decode_jwt_token(request.refresh_token)
    if payload:
        if payload["token_type"] != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        access_token = create_jwt_token({"sub": payload["sub"], "token_type": "access"})
        return RefreshTokenResponse(access_token=access_token, token_type="bearer")
    else:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
