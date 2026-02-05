from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ml.analytics import EcoBrain

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

def calculate_confidence(value, threshold):
    if value <= threshold:
        return 0.0
    ratio = value / threshold
    confidence = min(0.99, 0.7 + (ratio * 0.1))
    return round(confidence * 100, 2)

# --- CORE ROUTES ---
@app.post("/sensor/ingest")
def ingest_sensor_data(data: SensorReading):
    """ Detects Leaks/Waste and triggers Auto-Cutoff. """
    if not data.timestamp: data.timestamp = datetime.now()
    alert = None

    # 1. LEAK DETECTION
    if data.occupancy == 0 and data.water_flow > 2.0:
        prob = calculate_confidence(data.water_flow, 2.0)

        alert = {
            "id": len(alerts_log) + 1,
            "time": data.timestamp,
            "type": "CRITICAL_LEAK",
            "message": f"Leak Detected! Flow: {data.water_flow}L/m.",
            "probability_score": f"{prob}%",
            "action": "AUTO_CUTOFF (Solenoid Valve)",
            "status": "RESOLVED"
        }
        alerts_log.append(alert)

    # 2. ENERGY WASTE DETECTION
    elif data.occupancy == 0 and data.energy_load > 0.5:
        prob = calculate_confidence(data.energy_load, 0.5)

        alert = {
            "id": len(alerts_log) + 1,
            "time": data.timestamp,
            "type": "ENERGY_WASTE",
            "message": f"Energy Waste! Load: {data.energy_load} kW.",
            "probability_score": f"{prob}%",
            "action": "AUTO_CUTOFF (Smart Relay)",
            "status": "RESOLVED"
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
    current_time = datetime.now()
    total_water_needed = 12500.0  # Liters
    scheduled_time = "02:00 AM"
    duration_hours = total_water_needed / 5000

    energy_needed_kwh = (total_water_needed / 1000) * 0.5

    off_peak_rate = 6.80
    peak_rate = 10.20

    actual_cost = energy_needed_kwh * off_peak_rate
    potential_peak_cost = energy_needed_kwh * peak_rate
    savings = potential_peak_cost - actual_cost

    decision = {
        "date": current_time.strftime("%Y-%m-%d"),
        "timestamp": current_time,
        "total_water_pumped": f"{total_water_needed} L", # [NEW]
        "scheduled_time": scheduled_time,
        "duration": f"{round(duration_hours, 1)} Hours",
        "total_cost": f"₹{round(actual_cost, 2)}",       # [NEW] Actual Cost
        "money_saved": f"₹{round(savings, 2)}",
        "grid_status": "Off-Peak (Optimized)"
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
    return sorted(pump_history_log, key=lambda x: x['timestamp'], reverse=True)

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
        "probability_score": "100% (User Action)", # Manual is always 100%
        "action": "EXECUTED",
        "status": "MANUAL"
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