from fastapi import APIRouter
from app.schemas.info.output.battery_status import get_schema
from app.core.config import config
from app.services.info.battery import get_battery
from fastapi import HTTPException

batterystatusroute = APIRouter()


@batterystatusroute.get(
    "/battery-status", response_model=get_schema(config.custom_battery)
)
def get_battery_status():
    try:
        BatteryInfo = get_battery(config.custom_battery)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return BatteryInfo
