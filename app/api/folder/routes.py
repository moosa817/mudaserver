from fastapi import APIRouter
from app.api.folder.create_folder import createroute
from app.api.folder.rename_folder import renameroute
from app.api.folder.delete_folder import deleteroute
from app.api.folder.get_folder import getfolderroute
from app.api.folder.get_all_folders import getallfoldersroute
from app.api.folder.upload_folder import uploadroute
from app.api.folder.download_folder import download_folder_router

folderrouter = APIRouter()

folderrouter.include_router(createroute)
folderrouter.include_router(renameroute)
folderrouter.include_router(download_folder_router)
folderrouter.include_router(deleteroute)
folderrouter.include_router(getfolderroute)
folderrouter.include_router(getallfoldersroute)
folderrouter.include_router(uploadroute)
