from fastapi import APIRouter
from app.schemas.info.output.battery_status import get_schema
from app.core.config import config
from app.services.info.battery import get_battery
from fastapi import HTTPException
from app.api.dependencies import verify_basic_auth
from fastapi import Depends

batterystatusroute = APIRouter()


@batterystatusroute.get(
    "/battery-status", response_model=get_schema(config.custom_battery)
)
def get_battery_status(
    _: str = Depends(verify_basic_auth),
):
    try:
        BatteryInfo = get_battery(config.custom_battery)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return BatteryInfo
