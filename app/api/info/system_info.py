from fastapi import APIRouter
from app.schemas.info.output.system_info import SystemInfoResponse
from app.core.config import config
from app.services.info.SystemInfo import get_system_info
from app.api.dependencies import verify_basic_auth
from fastapi import Depends

systemstatusroute = APIRouter()


@systemstatusroute.get("/system-status", response_model=SystemInfoResponse)
def get_system_status(
    _: str = Depends(verify_basic_auth),
):
    return get_system_info()
