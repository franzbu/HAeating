# 🌡️ Home Assistant Heating Automation System

This repository contains a sophisticated, demand-driven heating control system built for **AppDaemon** and **Home Assistant**. Unlike traditional systems that run on fixed timers, this automation utilizes a **"Heating Claim" architecture** to optimize energy consumption and comfort levels.

---

## 🛠 System Architecture
The automation is split into two specialized layers to separate room logic from boiler hardware control:

1.  **`HeatingAutomation` (The Brain):** An instance runs for every room. It handles schedules, hysteresis, solar gain compensation, and calculates the "claim" for heat.
2.  **`HeatingPumpControl` (The Muscle):** A single central instance that monitors all room claims, calculates the optimal flow temperature, and interfaces with the boiler via Modbus.



---

## 🏠 Room-Level Logic (`HeatingAutomation`)

Each room functions as an independent agent. It monitors its own temperature and decides whether to "request" heat from the boiler.

### The "Heating Claim" (Hysteresis)
To prevent the boiler from cycling on and off too rapidly (which reduces hardware lifespan), the system uses a dual-threshold logic:

* **Upper Bound:** $Target - Margin$ (Default margin: $0.5^\circ C$)
* **Lower Bound:** $Target - \Delta$ (User-defined hysteresis)

| State | Condition | Result |
| :--- | :--- | :--- |
| **Heating Start** | `Current Temp < Lower Bound` | Claim → **ON** |
| **Maintaining** | `Lower Bound < Current Temp < Upper Bound` | State Persistent |
| **Heating Stop** | `Current Temp >= Upper Bound` | Claim → **OFF** |

### ☀️ Solar Compensation
If a room has high solar gain (e.g., south-facing windows), the automation proactively reduces the target temperature when it's warm outside.
* **Activation:** Triggers when outdoor temperature exceeds a defined threshold.
* **Dynamic Offset:** As outdoor heat increases, a percentage of the compensation factor is subtracted from the target.

### 🔥 Boost Mode
If a room temperature is significantly below the target (e.g., after a window was left open), the room calculates a **Boost Factor**. This tells the boiler to provide much hotter water temporarily to recover the room temperature as fast as possible.

---

## 🚂 Central Control (`HeatingPumpControl`)

The central controller monitors all `heating_claim_...` entities. If at least one room is claiming heat for longer than the `heating_claim_duration`, the boiler fires up.

### Dynamic Flow Temperature (Heating Curve)
The system doesn't use a fixed water temperature. It calculates the **Flow Target** using a linear heating curve:

$$T_{flow} = (-Adjustment \times T_{outdoor}) + Baseline_{0^\circ C} + Boost_{max} + Offset_{multi}$$

* **Baseline:** The required flow temperature when it is $0^\circ C$ outside.
* **Adjustment:** The "slope" of the curve.
* **Multi-room Offset:** For every additional room asking for heat, the flow temperature is nudged higher to account for increased thermal load.



---

## 📊 Monitoring & User Feedback

### Dashboard Intelligence
The system dynamically generates status messages for your Home Assistant UI:
* *“Heating starts at 06:00”*
* *“Heating stops at 22:30 tomorrow.”*
* *“Heating stops at next power cut ;)”* (For continuous 24/7 schedules).

### Safety Features
* **Modbus Health Check:** If the connection to the boiler's ESP32 Gateway fails, the system sends an emergency Telegram notification.
* **Auto-Revert:** If **Party Mode** is active but all radiator valves have closed (meaning the house is warm), the system automatically reverts to **Auto** to save fuel.

---

## 🚀 Setup & Configuration

### Required Home Assistant Entities
For the code to function, your Home Assistant instance must have the following entities configured per room:

| Entity Type | Naming Convention |
| :--- | :--- |
| `input_boolean` | `heating_claim_{location}` |
| `input_number` | `target_temp_{location}` |
| `input_select` | `heating_schedule_{location}` |
| `schedule` | `standard_{location}`, `holiday_{location}`, etc. |

### AppDaemon `apps.yaml` Example
```yaml
heating_livingroom:
  module: heating_automation
  class: HeatingAutomation
  solar_activation_temp: 15
  solar_peak_temp: 25

heating_pump_control:
  module: heating_pump_control
  class: HeatingPumpControl
  dependencies:
    - global_config
    - heating_livingroom
    - heating_bedroom
  telegram_id: "-100123456789"
