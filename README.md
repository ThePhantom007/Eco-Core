# 🌿 Eco Core OS

> **A complete adaptive sustainability ecosystem, where demand actively dictates supply.**

![EcoCore Dashboard Preview]([<img width="944" height="419" alt="image" src="https://github.com/user-attachments/assets/ca97e5a3-7eb7-4a6b-82a9-023df6d1e7e9" />
](https://github.com/user-attachments/assets/ca97e5a3-7eb7-4a6b-82a9-023df6d1e7e9))

## 📖 About The Project

Modern decentralized communities (campuses, residential societies) suffer from "Blind Utility Management". Resources are supplied based on rigid schedules, not actual need. This leads to HVAC and lights running in empty rooms (phantom loads), and pumps running during peak electricity hours, stressing the grid while "phantom leaks" in unoccupied zones go undetected.

**Eco Core OS** solves this by bridging the gap between hardware sensors and predictive AI. We introduce **Cross-Domain Intelligence**: using Occupancy Data (typically an energy metric) to optimize Water Supply. 

### The System is divided into two parts:
1. **Local Control Unit (IoT):** A local network that monitors occupancy. When no one is present in a room, but water is running, it will close the valve to prevent wastage.
2. **AI Agent (Machine Learning):** Predicts water demand based on occupancy history and schedules pumping during off-peak energy hours, leveraging cheaper electricity to save money.

---

## ✨ Key Features

* **⚡ Automated Hardware Intervention (The "Kill Switch"):** Eco Core goes beyond monitoring. Based on information from the AI model, the Python backend uses Modbus TCP/IP to actively command smart breakers and VFD pumps to take action. If an empty room is drawing power or leaking water, Python sends a signal to the smart relays to physically cut off the supply instantly.
* **🧠 Context-Aware AI:** Uses a `GradientBoostingRegressor` to understand the context of a room. 0.5kW of energy usage is "Normal" for 5 people, but an "Anomaly" for an empty room.
* **💧 Smart Water & Energy Arbitrage:** Decouples water pumping from peak electricity demand. The system calculates the exact water required for the next day and pumps it when grid electricity is cheapest.
* **🎮 Digital Twin Controller:** A built-in simulation engine that allows facility managers to run "What If" analyses. Replays historical data with new constraints to predict tank levels and potential shortages before implementation.
* **🔮 30-Day Budget Forecasting:** The AI simulates the next month of usage, factoring in weekends and busy periods, to project the facility's utility bill before it happens.
* **📱 Mobile App Alerts:** Real-time push notifications for anomalies with built-in manual override controls to take manual control of safety systems.

---

## 📊 Dashboard & User Interface
The Eco Core Dashboard is designed with a sleek glassmorphism aesthetic, providing an intuitive interface for facility managers. Key features include:
* **Real-Time Monitoring:** Live graphs of occupancy, energy usage, and water flow.
* **Anomaly Detection Alerts:** Visual indicators for any detected anomalies in resource usage.
* **Control Panel:** Manual override options for smart breakers and valves.
* **Forecasting Tools:** Interactive charts for budget forecasting and "What If" simulations.
* **Mobile Responsiveness:** Optimized for both desktop and mobile viewing, ensuring accessibility on the go.

---

## 🌍 Sustainability Impact
By implementing Eco Core OS, facilities can achieve:
* **Up to 30% Reduction in Energy Waste:** By cutting power to unoccupied rooms and optimizing pump schedules.
* **Up to 25% Reduction in Water Waste:** By detecting and preventing phantom leaks in real-time.
* **Cost Savings:** Leveraging off-peak electricity can reduce energy costs by up to 20% annually.
* **Carbon Footprint Reduction:** By optimizing resource usage, facilities can significantly reduce their carbon emissions, contributing to global sustainability goals.
* **Scalability:** The modular architecture allows for easy expansion to include additional resources like gas or renewable energy sources in the future.
* **Grid Decarbonization:** By shifting energy usage to off-peak hours, Eco Core helps reduce strain on the grid and promotes the use of cleaner energy sources.

## 🛠️ Tech Stack & Architecture

### Software (This Repository)
* **Backend:** Python, FastAPI
* **Machine Learning:** Scikit-Learn (Gradient Boosting Regressor), Pandas, Numpy, Joblib
* **Frontend Dashboard:** HTML5, CSS3 (Glassmorphism), Vanilla JavaScript, Chart.js
* **Mobile Client:** Android / Kotlin / Retrofit (Polled architecture)

### Hardware / IoT Integration (Conceptual Architecture)
* **Sensors (The Eyes):** ESP32 Microcontrollers, PIR/mmWave Radar for occupancy, and Water Flow Meters.
* **Actuators (The Muscle):** Smart Breakers for lighting/HVAC, Motorized Valves, and VFD Pumps. 
* **Protocols:** * **MQTT & Mosquitto Broker:** Lightweight messaging protocol used for low-latency data transmission from the sensors to the cloud.
  * **Modbus TCP/IP:** Used by the Python backend to interface directly with industrial hardware, allowing code to trigger physical breakers and valves.
* **Time-Series DB:** InfluxDB for storing high-frequency sensor data and electricity pricing patterns.

---

## 🚀 Getting Started (Local Development)

### Prerequisites
* Python 3.8+
* Git

### Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/ThePhantom007/Eco-Core.git](https://github.com/ThePhantom007/Eco-Core.git)
   cd Eco-Core
