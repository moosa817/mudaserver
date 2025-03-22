from pydantic import BaseModel
from typing import List


class SystemInfoResponse(BaseModel):
    cpu_name: str
    cpu_cores: int
    cpu_usage: float
    ram_total: float
    ram_used: float
    ram_free: float
    disk_total: float
    disk_used: float
    disk_free: float
    no_of_process: int
