from fastapi import APIRouter
from app.api.info.routes import inforouter
from app.api.auth.routes import authrouter

api_router = APIRouter()


api_router.include_router(inforouter, prefix="/info", tags=["Info"])
api_router.include_router(authrouter, prefix="/auth", tags=["Auth"])
