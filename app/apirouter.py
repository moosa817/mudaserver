from fastapi import APIRouter
from app.api.info.routes import inforouter


api_router = APIRouter()


api_router.include_router(inforouter, prefix="/info", tags=["Info"])
