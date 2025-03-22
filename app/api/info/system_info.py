from fastapi import APIRouter
from app.schemas.info.output.system_info import SystemInfoResponse
from app.core.config import config
from app.services.info.SystemInfo import get_system_info

systemstatusroute = APIRouter()


@systemstatusroute.get("/system-status", response_model=SystemInfoResponse)
def get_system_status():
    return get_system_info()
