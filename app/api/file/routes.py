from fastapi import APIRouter
from app.api.file.upload_file import upload_router
from app.api.file.rename_file import rename_router
from app.api.file.delete_file import delete_file_router
from app.api.file.edit_file import edit_router


filerouter = APIRouter()

filerouter.include_router(upload_router)
filerouter.include_router(rename_router)
filerouter.include_router(delete_file_router)
filerouter.include_router(edit_router)
