from fastapi import APIRouter
from app.api.info.routes import inforouter
from app.api.media.media import mediarouter

api_router = APIRouter()


api_router.include_router(inforouter, prefix="/info", tags=["Info"])
api_router.include_router(mediarouter, prefix="/media", tags=["Media"])
