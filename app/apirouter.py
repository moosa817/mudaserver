from fastapi import APIRouter
from app.api.info.routes import inforouter
from app.api.auth.routes import authrouter
from app.api.folder.routes import folderrouter
from app.api.file.routes import filerouter
from app.api.sync.sync_routes import syncrouter
from app.api.devices.device_routes import devicerouter

api_router = APIRouter()


api_router.include_router(inforouter, prefix="/info", tags=["Info"])
api_router.include_router(authrouter, prefix="/auth", tags=["Auth"])
api_router.include_router(folderrouter, prefix="/folder", tags=["Folder"])
api_router.include_router(filerouter, prefix="/file", tags=["File"])
api_router.include_router(syncrouter, prefix="/sync", tags=["Sync"])
api_router.include_router(devicerouter, prefix="/devices", tags=["Devices"])
