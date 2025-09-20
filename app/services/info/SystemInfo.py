import time
import psutil
from app.schemas.info.output.system_info import SystemInfoResponse
from cpuinfo import get_cpu_info


def get_system_info() -> dict:
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    cpu_info = get_cpu_info()
    cpu_name = cpu_info["brand_raw"]
    cpu_cores = psutil.cpu_count(logical=False)

    # Calculate uptime in seconds
    boot_time = psutil.boot_time()
    uptime_seconds = int(time.time() - boot_time)

    return SystemInfoResponse(
        cpu_name=cpu_name,
        cpu_cores=cpu_cores,
        cpu_usage=psutil.cpu_percent(),
        ram_total=round((memory.total / (1024**3)), 2),
        ram_used=round((memory.used / (1024**3)), 2),
        ram_free=round((memory.free / (1024**3)), 2),
        disk_free=round((disk.free / (1024**3)), 2),
        disk_total=round((disk.total / (1024**3)), 2),
        disk_used=round((disk.used / (1024**3)), 2),
        no_of_process=len(psutil.pids()),
        uptime_seconds=uptime_seconds,  # raw seconds
    )
