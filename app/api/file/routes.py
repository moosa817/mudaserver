from fastapi import APIRouter
from app.api.file.upload_file import upload_router


filerouter = APIRouter()

filerouter.include_router(upload_router)
