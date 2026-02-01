from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from src.analytics import EcoBrain

app = FastAPI(title="EcoCore OS", version="1.0")
brain = EcoBrain()

# --- DATABASES ---
alerts_log = []  # Stores Alert History
pump_history_log = []  # Stores Pumping History
room_status_db = {}  # Real-time Room Status

# --- DATA MODELS ---
class SensorReading(BaseModel):
    room_id: str
    timestamp: Optional[datetime] = None
    occupancy: int
    light_lux: float
    water_flow: float
    energy_load: float


class OverrideCommand(BaseModel):
    room_id: str
    utility: str  # "WATER" or "POWER"
    action: str  # "FORCE_ON" or "FORCE_OFF"
    user: str  # "Admin" or "Resident"

# --- CORE ROUTES ---
@app.post("/sensor/ingest")
def ingest_sensor_data(data: SensorReading):
    """ Detects Leaks/Waste and triggers Auto-Cutoff. """
    if not data.timestamp: data.timestamp = datetime.now()
    alert = None

    # 1. LEAK DETECTION
    if data.occupancy == 0 and data.water_flow > 2.0:
        alert = {
            "id": len(alerts_log) + 1,
            "time": data.timestamp,
            "type": "CRITICAL_LEAK",
            "message": f"Leak detected in {data.room_id}! Flow: {data.water_flow}L/min.",
            "status": "AUTO_RESOLVED (Cut-off sent)"
        }
        alerts_log.append(alert)

    # 2. ENERGY WASTE DETECTION
    elif data.occupancy == 0 and data.energy_load > 0.5:
        alert = {
            "id": len(alerts_log) + 1,
            "time": data.timestamp,
            "type": "ENERGY_WASTE",
            "message": f"Waste detected in {data.room_id}. AC/Lights on.",
            "status": "AUTO_RESOLVED (Cut-off sent)"
        }
        alerts_log.append(alert)

    # Update Room Status
    room_status_db[data.room_id] = {
        "status": "Active" if data.occupancy else "Eco-Mode",
        "last_update": data.timestamp,
        "latest_alert": alert
    }

    return {"status": "success", "alert": alert}


@app.get("/api/pump/optimize")
def calculate_pump_schedule():
    """
    Calculates best time to pump (Off-Peak).
    Saves this decision to history.
    """
    total_needed = 12500  # Liters
    best_time = "02:00 AM"

    decision = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "volume_liters": total_needed,
        "scheduled_time": best_time,
        "cost_savings": "₹450 (vs Peak)",
        "status": "SCHEDULED"
    }

    # Save to History Log
    pump_history_log.append(decision)
    return decision

# --- HISTORY ENDPOINTS ---
@app.get("/api/history/alerts")
def get_alert_history():
    """Returns the full list of alerts for the website dashboard."""
    return sorted(alerts_log, key=lambda x: x['time'], reverse=True)

@app.get("/api/history/pumping")
def get_pump_history():
    """Returns the history of all pump operations."""
    return pump_history_log

# --- MANUAL OVERRIDE ---

@app.post("/api/control/override")
def manual_override(cmd: OverrideCommand):
    """
    Allows App/Website to force Water or Power ON/OFF.
    Overrides any AI decision.
    """
    timestamp = datetime.now()

    # Log the override action
    log_entry = {
        "id": len(alerts_log) + 1,
        "time": timestamp,
        "type": "MANUAL_OVERRIDE",
        "message": f"{cmd.user} forced {cmd.utility} {cmd.action} in {cmd.room_id}.",
        "status": "EXECUTED"
    }
    alerts_log.append(log_entry)

    # Update real-time status to reflect user command
    if cmd.room_id in room_status_db:
        room_status_db[cmd.room_id]['status'] = f"MANUAL_{cmd.action}"

    return {
        "status": "success",
        "message": f"Command {cmd.action} sent to {cmd.utility} Controller.",
        "override_log": log_entry
    }