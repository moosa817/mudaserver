import psutil
from app.schemas.info.output.battery_status import get_schema,CustomBatteryStatus
import subprocess


def get_battery(custom_battery:bool)->dict:
    schema = get_schema(custom_battery)
    if not custom_battery:
        battery = psutil.sensors_battery()
        return schema(battery_status="charging" if battery.power_plugged else "discharging",
                      battery_percentage=round(battery.percent),
                      minutes_remaining=round(battery.secsleft/60))
        
    
    # custom battery status for linux upower
    result = subprocess.run(["upower -e | grep BAT"],stdout=subprocess.PIPE,shell=True)
    
    battery_paths = result.stdout.decode("utf-8").strip().split("\n")
    
    mybatteries = []
    for battery_path in battery_paths:
        state = subprocess.run([f"upower -i {battery_path}"+ " | awk '/state:/ {print $2}'"],stdout=subprocess.PIPE,shell=True)
        percentage = subprocess.run([f"upower -i {battery_path}"+ " | awk '/percentage:/ {print $2}'"],stdout=subprocess.PIPE,shell=True)
        capacity = subprocess.run([f"upower -i {battery_path}"+ " | awk '/capacity:/ {print $2}'"],stdout=subprocess.PIPE,shell=True)
        time = subprocess.run([f"upower -i {battery_path}"+ " | awk '/time to empty:/ {print $4, $5, $6}'"],stdout=subprocess.PIPE,shell=True)
        
        charging_state = state.stdout.decode("utf-8").strip().strip("%")
        percent = int(percentage.stdout.decode("utf-8").strip().strip("%"))
        health = round(float(capacity.stdout.decode("utf-8").strip().strip("%")))
        time =time.stdout.decode("utf-8").strip()
        if time == "":
            time = 0
            
        mybatteries.append(CustomBatteryStatus(battery_status=charging_state,
                                               battery_percentage=percent,
                                               minutes_remaining=time,
                                               health_status=health))
    return schema(batteries=mybatteries)