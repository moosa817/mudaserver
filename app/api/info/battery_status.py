from fastapi import APIRouter
from app.schemas.info.output.battery_status import get_schema
from app.core.config import config
from app.services.info.battery import get_battery

batterystatusroute = APIRouter()

@batterystatusroute.get('/battery-status',response_model=get_schema(config.custom_battery))
def get_battery_status():
    BatteryInfo = get_battery(config.custom_battery)
    return BatteryInfo