from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from ml.analytics import EcoBrain
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI(title="EcoCore OS", version="1.0")
brain = EcoBrain()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

app.mount("/static", StaticFiles(directory="website/static"), name="static")
templates = Jinja2Templates(directory="website/templates")

# --- DATABASES ---
alerts_log = []  # Stores Alert History
pump_history_log = []  # Stores Pumping History
battery_history_log = []  # Stores Battery Charging History
room_status_db = {}  # Real-time Room Status

def seed_demo_data():
    """ Generates 7 days of history so the Dashboard Graphs look impressive immediately. """
    now = datetime.now()
    for i in range(7):
        # Go back 'i' days (0 = Today, 1 = Yesterday, etc.)
        past_date = now - timedelta(days=i)
        date_str = past_date.strftime("%Y-%m-%d")

        # --- 1. Water Pump Data ---
        # Vary water usage slightly (between 11,000 and 13,000 L)
        daily_water = random.uniform(11000, 13000)

        # Cost Math
        energy_kwh = (daily_water / 1000) * 0.5
        actual_cost = energy_kwh * 6.80  # Off-Peak
        peak_cost = energy_kwh * 10.20  # Peak
        savings = peak_cost - actual_cost

        pump_history_log.append({
            "date": date_str,
            "timestamp": past_date.replace(hour=2, minute=0),
            "total_water_pumped": f"{int(daily_water)} L",
            "scheduled_time": "02:00 AM",
            "duration": f"{round(daily_water / 5000, 1)} Hours",
            "total_cost": round(actual_cost, 2),  # Store as NUMBER for graphing
            "peak_cost_comparison": round(peak_cost, 2),  # Store for graphing
            "money_saved": f"₹{round(savings, 2)}",
            "grid_status": "Off-Peak"
        })

        # --- 2. Battery Data ---
        # Vary battery needs slightly
        daily_charge = random.uniform(65, 80)  # kWh

        batt_actual = daily_charge * 6.80
        batt_peak = daily_charge * 10.20
        batt_savings = batt_peak - batt_actual

        battery_history_log.append({
            "date": date_str,
            "timestamp": past_date.replace(hour=1, minute=0),
            "energy_added": f"{int(daily_charge)} kWh",
            "initial_charge": "20%",
            "target_charge": "100%",
            "total_cost": round(batt_actual, 2),  # Store as NUMBER
            "peak_cost_comparison": round(batt_peak, 2),  # Store for graphing
            "money_saved": f"₹{round(batt_savings, 2)}",
            "grid_status": "Off-Peak"
        })

        # Alerts
    alerts_log.append({
        "id": 101, "time": now - timedelta(hours=3),
        "type": "CRITICAL_LEAK", "message": "Leak in Restroom 3B",
        "probable_wastage": "450 Liters", "estimated_savings": "₹22.95",
        "probability_score": "98.5%", "action": "AUTO_CUTOFF", "status": "RESOLVED"
    })
    alerts_log.append({
        "id": 102, "time": now - timedelta(minutes=15),
        "type": "ENERGY_WASTE", "message": "Lecture Hall 101 AC on",
        "probable_wastage": "2.5 kWh", "estimated_savings": "₹25.50",
        "probability_score": "94.2%", "action": "AUTO_CUTOFF", "status": "RESOLVED"
    })

seed_demo_data()

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
@app.get("/dashboard")
def dashboard(request: Request):
    """Serves the main website dashboard."""
    return templates.TemplateResponse("dashboard.html", {"request": request})
@app.post("/sensor/ingest")
def ingest_sensor_data(data: SensorReading):
    """ Detects Leaks/Waste and triggers Auto-Cutoff. """
    if not data.timestamp: data.timestamp = datetime.now()
    alert = None

    # 1. LEAK DETECTION
    if data.occupancy == 0 and data.water_flow > 2.0:
        prob = calculate_confidence(data.water_flow, 2.0)
        wasted_liters = data.water_flow * 60
        # Cost: Liters/1000 * 0.5kWh/m3 * Peak Rate (10.20)
        est_cost = (wasted_liters / 1000) * 0.5 * 10.20

        alert = {
            "id": len(alerts_log) + 1,
            "time": data.timestamp,
            "type": "CRITICAL_LEAK",
            "message": f"Leak Detected! Flow: {data.water_flow}L/m.",
            "probable_wastage": f"{int(wasted_liters)} Liters",
            "estimated_savings": f"₹{round(est_cost, 2)}",
            "probability_score": f"{prob}%",
            "action": "AUTO_CUTOFF (Solenoid Valve)",
            "status": "RESOLVED"
        }
        alerts_log.append(alert)

    # 2. ENERGY WASTE DETECTION
    elif data.occupancy == 0 and data.energy_load > 0.5:
        prob = calculate_confidence(data.energy_load, 0.5)
        wasted_kwh = data.energy_load * 1.0
        est_cost = wasted_kwh * 10.20  # Peak Rate

        alert = {
            "id": len(alerts_log) + 1,
            "time": data.timestamp,
            "type": "ENERGY_WASTE",
            "message": f"Energy Waste! Load: {data.energy_load} kW.",
            "probable_wastage": f"{round(wasted_kwh, 2)} kWh",
            "estimated_savings": f"₹{round(est_cost, 2)}",
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
        "total_water_pumped": f"{total_water_needed} L",
        "scheduled_time": scheduled_time,
        "duration": f"{round(duration_hours, 1)} Hours",
        "total_cost": f"₹{round(actual_cost, 2)}",
        "money_saved": f"₹{round(savings, 2)}",
        "grid_status": "Off-Peak (Optimized)"
    }

    # Save to History Log
    pump_history_log.append(decision)
    return decision


@app.get("/api/battery/optimize")
def calculate_battery_schedule():
    """ ENERGY ARBITRAGE: Charges battery during cheap hours. """
    current_time = datetime.now()

    # 1. Simulate Battery State
    battery_capacity = 100.0  # kWh (Powerwall-sized commercial unit)
    current_charge = 30.0  # kWh (Average based on usage patterns, 30% charged)

    # 2. Calculate Needs
    energy_needed_kwh = battery_capacity - current_charge  # 70 kWh needed

    # 3. Cost Math (DERC Tariffs)
    off_peak_rate = 6.80  # Night rate
    peak_rate = 10.20  # Day rate

    actual_cost = energy_needed_kwh * off_peak_rate
    potential_peak_cost = energy_needed_kwh * peak_rate
    savings = potential_peak_cost - actual_cost

    # 4. Schedule (Charge Speed)
    # Assume 10kW Charger -> 70kWh / 10kW = 7 Hours
    duration_hours = energy_needed_kwh / 10.0

    decision = {
        "date": current_time.strftime("%Y-%m-%d"),
        "timestamp": current_time,
        "initial_charge": "30%",
        "target_charge": "100%",
        "energy_added": f"{energy_needed_kwh} kWh",
        "scheduled_time": "01:00 AM",
        "duration": f"{round(duration_hours, 1)} Hours",
        "total_cost": f"₹{round(actual_cost, 2)}",
        "money_saved": f"₹{round(savings, 2)}",
        "grid_status": "Off-Peak (Optimized)"
    }

    # Save to History
    battery_history_log.append(decision)

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

@app.get("/api/history/battery")
def get_battery_history():
    return sorted(battery_history_log, key=lambda x: x['timestamp'], reverse=True)

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