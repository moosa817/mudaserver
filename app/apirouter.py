from fastapi import APIRouter
from app.api.info.battery_status import batterystatusroute

api_router = APIRouter()


api_router.include_router(batterystatusroute,prefix="/info",tags=["Info"])
