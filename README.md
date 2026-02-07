Code is in advanced state; however, the documentation below is not. I might improve it at a later stage if there is any user interest.



 🌡️ Home Assistant Heating Automation System

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
```


# 🌡️ Heating Automation: User Manual

This guide covers the configuration and operation of the Smart Heating System, from global boiler settings to individual room controls.

---

<img width="369" height="274" alt="Screenshot 2026-02-07 at 10 32 44 AM" src="https://github.com/user-attachments/assets/7badd294-1c8c-4a2e-b169-c7a4e3e969bf" />


## ⚙️ Main Heating Settings (Global)

These settings control the overall behavior of the central heating pump and flow temperature calculations.

* **Main Switch:** Global toggle to enable or disable the entire heating automation.
* **Heating Margin:** Defines the stop trigger. Heating stops when `Current Temp >= Target Temp - Heating Margin`.
* **Cooldown:** Minimum time between switching the heating pump on or off (protects mechanical components from wear).
* **Claim Duration:** Delay before a dashboard change takes effect (filters out temporary temperature "jitter").
* **Boost Threshold:** Activation trigger for high-output heating. Boost starts if `Current Temp < Target Temp - Boost Threshold`.
* **Boost Factor:** Determines the flow temperature increase: 
    * $$Flow\ Increase = (Target\ Temp - Current\ Temp) \times Boost\ Factor$$
* **Baseline at $0^\circ C$:** The base flow temperature when the outside temperature is exactly $0^\circ C$.
* **Curve Adjustment:** The factor by which flow temperature is increased or decreased relative to changes in outside temperature.
* **Max Flow Temp:** The safety ceiling for water temperature (prevents damage to floor plaster/screed).

---

## 🏠 Individual Room Settings

Each room is managed via a dedicated dashboard view containing the following data points:

### Standard View

<img width="385" height="112" alt="Screenshot 2026-02-07 at 10 35 32 AM" src="https://github.com/user-attachments/assets/0c0b9c39-e116-45f0-83b4-16c06f6ccf9b" />

* **Live Metrics:** Current temperature, heating valve opening percentage, and humidity.
* **Targeting:** Current heating target temperature and the name of the currently active schedule.
* **Event Info:** Swipe horizontally to view detailed information regarding the current or next heating event.
<img width="395" height="108" alt="Screenshot 2026-02-07 at 10 36 04 AM" src="https://github.com/user-attachments/assets/b0c5bb49-fd8e-4411-a793-c64a77b5ef8e" />



### Advanced Room Parameters

* **Boost Status:** Displays if boost is active and how many degrees the flow temperature is being increased by this specific room.
<img width="394" height="112" alt="Screenshot 2026-02-07 at 10 36 30 AM" src="https://github.com/user-attachments/assets/2b0aed9d-7890-4431-b1e4-91fc5476c28a" />
  

* **Heating Delta ($\Delta$):** The "Start" trigger. Heating turns on when the temperature drops below `Target Temp - Delta`.
    * *Control:* Tap the card/icon to adjust; long-tap for larger increments.
<img width="407" height="113" alt="Screenshot 2026-02-07 at 10 37 04 AM" src="https://github.com/user-attachments/assets/4fd796f9-9c4a-43ab-8d84-e34d37a3c926" />



* **Base Temp:** The "Background" temperature used outside of scheduled heating events. This allows for passive heating to prevent the room from getting too cold.
<img width="375" height="105" alt="Screenshot 2026-02-07 at 10 37 27 AM" src="https://github.com/user-attachments/assets/3b2c6b25-d1bf-4f1d-b902-28566b1f9d08" />


* **Heat Temp:** The default target temperature used during active schedule events if no specific temperature is defined within the schedule itself.
<img width="377" height="97" alt="Screenshot 2026-02-07 at 10 37 49 AM" src="https://github.com/user-attachments/assets/f8f194f5-165b-42b0-a338-0a6951cd8fb9" /> 
---

## 📅 Scheduling System

The schedules are the heart of the automation. The system follows the logic of the currently selected schedule to determine if heating is allowed.

### Schedule Types
1.  **Standard:** Your everyday routine.
<img width="380" height="102" alt="Screenshot 2026-02-07 at 10 40 48 AM" src="https://github.com/user-attachments/assets/ca37c6a0-a288-449f-bbbb-2a8408b2c05c" />
2.  **Holiday:** Energy-saving mode for when you are away.
<img width="382" height="106" alt="Screenshot 2026-02-07 at 10 41 16 AM" src="https://github.com/user-attachments/assets/08e5b9b5-98db-4060-8458-8154720a922e" />

3.  **Party:** Overrides timers for extended comfort.
4.  **Temporary:** Short-term adjustments.
5.  **Off:** Frost protection only (Target set to $5^\circ C$).




### Interaction & Controls
* **Cycle Schedules:** Tap the main schedule card to cycle forward; tap the icon to cycle backward.
* **Activation:** Swipe to a schedule and **long-tap** to make it active.
* **Quick Toggle:** * Long-tap the main card to switch to **Off**. 
    * If already Off, long-tap to return to **Standard**.
* **Shortcuts:** Long-tap on temperature, valve state, or humidity to jump directly to **Holiday**, **Party**, or **Temporary** modes.
* **Visual Indicators:** A **green icon** signifies the schedule is currently active; a **gray icon** signifies it is inactive.

---

## 🎨 Status Color Guide

The dashboard uses color-coding to signal the current state of the heating demand and the central pump (HK2) status.

| Color | Logic / Condition | System State |
| :--- | :--- | :--- |
| **Red** | Heating Claim Active | Boiler in **Party** or **Extra-Heating** mode |
| **Purple** | Heating Claim Active | Boiler is currently **OFF** |
| **Orange** | No Claim + Temp < Target - 0.5 | Boiler in **Party** or **Extra-Heating** mode |
| **Green** | No Claim + Temp < Target - 0.5 | Boiler in **Automatic** mode |
| **Blue** | No Claim + Temp < Target - 0.5 | Boiler is currently **OFF** |
| **Yellow** | Current Temp > Target - 0.5 | Room is warm (Target > 5) |
| **Gray** | "No" in `next_event` text | No future heating planned (Schedule **Off**) |
| **Light Blue** | Else | Standby / Neutral |
