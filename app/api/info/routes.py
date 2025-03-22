from fastapi import APIRouter
from app.api.info.battery_status import batterystatusroute
from app.api.info.system_info import systemstatusroute

inforouter = APIRouter()

inforouter.include_router(batterystatusroute)
inforouter.include_router(systemstatusroute)
