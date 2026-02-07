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
    """ Generates 31 days of history. """
    now = datetime.now()
    alerts_log.clear()
    pump_history_log.clear()
    battery_history_log.clear()

    for i in range(31):
        # Go back 'i' days
        past_date = now - timedelta(days=30-i) # Start 30 days ago, end today
        date_str = past_date.strftime("%Y-%m-%d")
        is_weekend = past_date.weekday() >= 5

        # --- 1. Water Pump Data ---
        if is_weekend:
            daily_water = random.uniform(2000, 4000) # Low usage
        else:
            daily_water = random.uniform(11000, 14000) # High usage

        energy_kwh = (daily_water / 1000) * 0.5
        actual_cost = energy_kwh * 6.80  # Off-Peak
        peak_cost = energy_kwh * 10.20   # Peak
        savings = peak_cost - actual_cost

        pump_history_log.append({
            "date": date_str,
            "timestamp": past_date.replace(hour=2, minute=0),
            "total_water_pumped": f"{int(daily_water)} L",
            "scheduled_time": "02:00 AM",
            "duration": f"{round(daily_water/5000, 1)} Hours",
            "total_cost": round(actual_cost, 2),
            "peak_cost_comparison": round(peak_cost, 2),
            "money_saved": f"₹{round(savings, 2)}",
            "grid_status": "Off-Peak"
        })

        # --- 2. Battery Data ---
        if is_weekend:
            daily_charge = random.uniform(10, 30) # Maintaince charge
        else:
            daily_charge = random.uniform(70, 90) # Full cycle

        batt_actual = daily_charge * 6.80
        batt_peak = daily_charge * 10.20
        batt_savings = batt_peak - batt_actual

        battery_history_log.append({
            "date": date_str,
            "timestamp": past_date.replace(hour=1, minute=0),
            "energy_added": f"{int(daily_charge)} kWh",
            "initial_charge": "20%",
            "target_charge": "100%",
            "total_cost": round(batt_actual, 2),
            "peak_cost_comparison": round(batt_peak, 2),
            "money_saved": f"₹{round(batt_savings, 2)}",
            "grid_status": "Off-Peak"
        })

    # Add a few "Recent" alerts so the table isn't empty
    alerts_log.append({
        "id": 101, "time": now - timedelta(hours=3),
        "type": "CRITICAL_LEAK", "message": "Leak in Restroom 3B",
        "probable_wastage": "450 Liters", "estimated_savings": "₹22.95",
        "probability_score": "98.5%", "action": "AUTO_CUTOFF", "status": "RESOLVED"
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
    current_hour = data.timestamp.hour

    # WATER THRESHOLD
    predicted_water_normal = brain.predict_demand(current_hour, data.occupancy, data.light_lux)
    water_threshold = (predicted_water_normal * 1.5) + 1.0  # Safety buffer

    # ENERGY THRESHOLD (Context Calculated)
    expected_energy_load = (data.occupancy * 0.2) + 0.2
    energy_threshold = expected_energy_load * 1.2  # 20% Buffer for spikes

    alert = None

    # --- DYNAMIC WATER LEAK DETECTION ---
    if data.water_flow > water_threshold:
        deviation = data.water_flow - predicted_water_normal
        prob = min(99.9, (deviation / water_threshold) * 100)

        wasted_liters = (data.water_flow - predicted_water_normal) * 60
        est_cost = (wasted_liters / 1000) * 0.5 * 10.20

        alert = {
            "id": len(alerts_log) + 1,
            "time": data.timestamp,
            "type": "AI_ANOMALY_WATER",
            "message": f"Abnormal Water Flow! Expected {predicted_water_normal}L, Got {data.water_flow}L.",
            "probable_wastage": f"{int(wasted_liters)} Liters",
            "estimated_savings": f"₹{round(est_cost, 2)}",
            "probability_score": f"{round(prob, 1)}%",
            "action": "AUTO_CUTOFF",
            "status": "RESOLVED"
        }
        alerts_log.append(alert)

    # --- DYNAMIC ENERGY WASTE DETECTION ---
    elif data.energy_load > energy_threshold:

        # Calculate Deviation
        deviation = data.energy_load - expected_energy_load

        # If deviation is small (just noise), ignore. If large (AC left on), Alert.
        if deviation > 0.5:
            prob = min(99.9, (deviation / energy_threshold) * 100)

            wasted_kwh = deviation * 1.0
            est_cost = wasted_kwh * 10.20  # Peak Rate

            alert = {
                "id": len(alerts_log) + 1,
                "time": data.timestamp,
                "type": "AI_ANOMALY_ENERGY",
                "message": f"Abnormal Energy Spike! Expected {round(expected_energy_load, 1)}kW, Got {data.energy_load}kW.",
                "probable_wastage": f"{round(wasted_kwh, 2)} kWh",
                "estimated_savings": f"₹{round(est_cost, 2)}",
                "probability_score": f"{round(prob, 1)}%",
                "action": "AUTO_CUTOFF",
                "status": "RESOLVED"
            }
            alerts_log.append(alert)

    room_status_db[data.room_id] = {
    "pump_on": True,
    "power_on": True,
    "last_update": data.timestamp,
    "latest_alert": alert
}

    return {
        "status": "success",
        "alert": alert,
        "debug": {
            "ai_water_normal": predicted_water_normal,
            "calc_energy_normal": expected_energy_load
        }
    }


@app.get("/api/pump/optimize")
def calculate_pump_schedule():
    """
    Calculates best time to pump (Off-Peak).
    Saves this decision to history.
    """
    current_time = datetime.now()
    # We multiply by 60 mins * 8 hours to simulate a full night's buffer fill.
    predicted_flow_per_min = brain.predict_demand(hour=2, occupancy=0, light_lux=0)

    # If the model predicts 0 (unlikely but possible), fallback to a safe base load
    if predicted_flow_per_min <= 0:
        predicted_flow_per_min = 20.0  # Safety fallback

    total_water_needed = predicted_flow_per_min * 60 * 8 # Liters

    energy_needed_kwh = (total_water_needed / 1000) * 0.5

    off_peak_rate = 6.80
    peak_rate = 10.20

    actual_cost = energy_needed_kwh * off_peak_rate
    potential_peak_cost = energy_needed_kwh * peak_rate
    savings = potential_peak_cost - actual_cost

    decision = {
        "date": current_time.strftime("%Y-%m-%d"),
        "timestamp": current_time,
        "total_water_pumped": f"{int(total_water_needed)} L",
        "scheduled_time": "02:00 AM",
        "duration": f"{round(total_water_needed / 5000, 1)} Hours",
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

@app.get("/api/forecast/budget")
def forecast_budget():
    """
    FUTURE FORECASTING: Simulates the next 30 days to predict the monthly bill.
    Used for 'Budget vs Actual' analysis.
    """
    today = datetime.now()
    total_predicted_water = 0
    total_predicted_cost = 0

    # Simulate next 30 days
    for day in range(1, 31):
        future_date = today + timedelta(days=day)
        is_weekend = future_date.weekday() >= 5

        # Assumption: Weekends are empty (0 occ), Weekdays are busy (50 occ)
        sim_occupancy = 0 if is_weekend else 50
        sim_light = 0 if is_weekend else 500

        # Ask AI for daily demand (Summing 8 active hours for simplicity)
        # We sample 10 AM as a representative "Peak Hour" for the model
        if brain:
            # AI Available: Ask for prediction
            hourly_flow = brain.predict_demand(hour=10, occupancy=sim_occupancy, light_lux=sim_light)
        else:
            hourly_flow = (sim_occupancy * 0.2) + 2.0

        # Daily Water = Hourly Flow * 10 active hours
        daily_water = hourly_flow * 60 * 10
        total_predicted_water += daily_water

        # Cost Math (Assumes mixed peak/off-peak usage)
        # 50% Peak (₹10.20), 50% Off-Peak (₹6.80) -> Avg ₹8.50
        daily_kwh = (daily_water / 1000) * 0.5
        daily_cost = daily_kwh * 8.50

        total_predicted_cost += daily_cost

    return {
        "forecast_period": "Next 30 Days",
        "projected_water_usage": f"{int(total_predicted_water):,} Liters",
        "projected_bill": f"₹{int(total_predicted_cost):,}",
        "status": "Under Budget" if total_predicted_cost < 5000 else "Over Budget",
        "recommendation": "Maintain current schedule" if total_predicted_cost < 5000 else "Reduce peak pumping"
    }

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

@app.get("/api/status/{room_id}")
def get_room_status(room_id: str):

    room = room_status_db.get(room_id, {
        "pump_on": False,
        "power_on": False
    })

    return room


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
        if cmd.action == "ON" and cmd.utility == "WATER":
            room_status_db[cmd.room_id]['pump_on'] = True
        
        elif cmd.action == "OFF" and cmd.utility == "WATER":
            room_status_db[cmd.room_id]['pump_on'] = False

        elif cmd.action == "ON" and cmd.utility == "POWER": 
            room_status_db[cmd.room_id]['power_on'] = True

        elif cmd.action == "OFF" and cmd.utility == "POWER":
        
            room_status_db[cmd.room_id]['power_on'] = False
        

    return {
        "status": "success",
        "message": f"Command {cmd.action} sent to {cmd.utility} Controller.",
        "override_log": log_entry
    }