from fastapi import APIRouter
from app.api.auth.token import tokenroute
from app.api.auth.refresh import refreshroute

authrouter = APIRouter()

authrouter.include_router(tokenroute)
authrouter.include_router(refreshroute)
