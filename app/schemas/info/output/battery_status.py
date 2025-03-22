from pydantic import BaseModel
from typing import List
from app.core.config import config


class CustomBatteryStatus(BaseModel):
    battery_status: str
    battery_percentage: int
    time_remaining: str
    health_status: int


def get_schema(custom):
    class BatteryStatusResponse(BaseModel):
        battery_status: str
        battery_percentage: int
        minutes_remaining: int

    class CustomBatteryStatusResponse(BaseModel):
        batteries: List[CustomBatteryStatus]

    return CustomBatteryStatusResponse if custom else BatteryStatusResponse
