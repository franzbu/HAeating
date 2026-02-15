


# 🌡️ Home Assistant Heating

This repository contains a heating control system built with **AppDaemon** (Python) for **Home Assistant**.

Why AppDaemon? AppDaemon has been chosen for its ability to use Python without restrictions (other than PyScript), including the possibility of creating instances of classes. This makes it possible to create an instance of RoomDemandCalculator for each room, allowing for efficient and straightforward code. 

## 🛠 System Architecture
The heating automation is split into three specialized layers:  
  (1) Room Level: RoomDemandCalculator
  (2 Central Heating Control: HeatSupplyManager
  (3) Hardware Interface: connects to the actual hardware, for example, a Froeling SP Dual


1.  **`RoomDemandCalculator` (The Brain):** An instance of this app runs for every room. It handles schedules, hysteresis, solar gain compensation, boost demands, and calculates the heat claim for the room.
   
2.  **`HeatSupplyManager` (The Muscle):** HeatSupplyManager acts as control center for juggling the heating demands for all rooms. Heating is initiated by writing the target flow temperature to the HA Helper `input_number.target_flow_temp` (heating stops by writing 0).
   
3. The hardware interface listens to `input_number.target_flow_temp` and initiates heating in accordance with the value in `input_number.target_flow_temp`. 

---

## 1. 🏠 Room-Level Logic (`RoomDemandCalculator`)

Each room functions as an independent agent. It monitors its own temperature and decides whether to "request" heat from the boiler.

### ☀️ Solar Compensation
If a room has high solar gain (e.g., south-facing windows), the automation proactively reduces the target temperature when it's warm outside.
* **Activation:** Triggers when outdoor temperature exceeds a defined threshold.
* **Dynamic Offset:** As outdoor heat increases, a percentage of the compensation factor is subtracted from the target.

### 🔥 Boost Mode
If a room temperature is significantly below the target (e.g., after a window was left open), the room calculates a **Boost Factor**. This tells the boiler to provide much hotter water temporarily to recover the room temperature as fast as possible.


---

### Dashboard Intelligence
The system dynamically generates status messages for your Home Assistant UI:
* *“Heating starts at 06:00”*
* *“Heating stops at 22:30 tomorrow.”*
* *“Heating stops at next power cut ;)”* (For continuous 24/7 schedules).

### Safety Features
* **Modbus Health Check:** If the connection to the boiler's ESP32 Gateway fails, the system sends an emergency Telegram notification.
* **Auto-Revert:** If **Party Mode** is active but all radiator valves have closed (meaning the house is warm), the system automatically reverts to **Auto** to save fuel.

---

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
  class: RoomDemandCalculator
  solar_activation_temp: 15
  solar_peak_temp: 25

heating_pump_control:
  module: heating_pump_control
  class: HeatSupplyManager
  dependencies:
    - global_config
    - heating_livingroom
    - heating_bedroom
  telegram_id: "-100123456788"
```

---

<img width="369" height="274" alt="Screenshot 2026-02-07 at 10 32 44 AM" src="https://github.com/user-attachments/assets/7badd294-1c8c-4a2e-b169-c7a4e3e969bf" />


### ⚙️ Main Heating Settings (Global)

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

### 🏠 Individual Room Settings

Each room is managed via a dedicated dashboard view containing the following data points:

#### Standard View

<img width="385" height="112" alt="Screenshot 2026-02-07 at 10 35 32 AM" src="https://github.com/user-attachments/assets/0c0b9c39-e116-45f0-83b4-16c06f6ccf9b" />

* **Live Metrics:** Current temperature, heating valve opening percentage, and humidity.
* **Target temp:** Current heating target temperature and the name of the currently active schedule.
* **Event Info:** Swipe horizontally to view detailed information regarding the current or next heating event.
<img width="395" height="108" alt="Screenshot 2026-02-07 at 10 36 04 AM" src="https://github.com/user-attachments/assets/b0c5bb49-fd8e-4411-a793-c64a77b5ef8e" />



#### Advanced Room Parameters

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

### 📅 Scheduling System

The schedules are the heart of the automation. The system follows the logic of the currently selected schedule to determine if heating is allowed.

#### Schedule Types
1.  **Standard:** Your everyday routine.
<img width="380" height="102" alt="Screenshot 2026-02-07 at 10 40 48 AM" src="https://github.com/user-attachments/assets/ca37c6a0-a288-449f-bbbb-2a8408b2c05c" />

2.  **Holiday:** Energy-saving mode for when you are away.
<img width="382" height="106" alt="Screenshot 2026-02-07 at 10 41 16 AM" src="https://github.com/user-attachments/assets/08e5b9b5-98db-4060-8458-8154720a922e" />

3.  **Party:** Overrides timers for extended comfort.
4.  **Temporary:** Short-term adjustments.
5.  **Off:** Frost protection only (Target set to $5^\circ C$).




#### Interaction & Controls
* **Cycle Schedules:** Tap the main schedule card to cycle forward; tap the icon to cycle backward.
* **Activation:** Swipe to a schedule and **long-tap** to make it active.
* **Quick Toggle:** * Long-tap the main card to switch to **Off**. 
    * If already Off, long-tap to return to **Standard**.
* **Shortcuts:** Long-tap on temperature, valve state, or humidity to jump directly to **Holiday**, **Party**, or **Temporary** modes.
* **Visual Indicators:** A **green icon** signifies the schedule is currently active; a **gray icon** signifies it is inactive.

---

### 🎨 Status Color Guide

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




---

## 2. 🚂 Central Control (`HeatSupplyManager`)

The central controller monitors all rooms; if at least one room is claiming heat, heating is initiated.

### Dynamic Flow Temperature (Heating Curve)
The system doesn't use a fixed water temperature. It calculates the **Flow Target** using a linear heating curve:

$$T_{flow} = (-Adjustment \times T_{outdoor}) + Baseline_{0^\circ C} + Boost_{max} + Offset_{multi}$$

* **Baseline:** The required flow temperature when it is $0^\circ C$ outside.
* **Adjustment:** The "slope" of the curve.
* **Multi-room Offset:** For every additional room asking for heat, the flow temperature is nudged higher to account for increased thermal load.


---
## 3. Connection to Heating Hardware

The principle is simple: HA's helper `input_number.target_flow_temp` signals heating demand when it contains the required flow temperature; it signals no heating demand if it is set to `0`. This respository contains two examples how this can be used to connect the actual heating device, which can be a thermal heat pump, wood boiler, ... 

### (A) Froeling wood boiler, using [GyroGearl00se's HA integration for Froeling](https://github.com/GyroGearl00se/ha_froeling_lambdatronic_modbus) `ha_froeling_lambdatronic_modbus`.

The example can be seen [here](https://github.com/franzbu/HomeAssistantHeating/blob/main/AppDaemon/heating_froeling_modbus.py).

---

### (B) Froeling wood boiler, using an ESP32

The ESP is programmed to listen to changes to HA's input_number.target_flow_temp and starts (when value is set to the required flow temp) and stops (when value is set to 0) heating accordingly. The ESP is connected to HA via ethernet (also Wifi or other wireless communication will work; however, ethernet is recommended for its reliability) and to the Froeling boiler via Modbus.

<img width="698" height="478" alt="Screenshot 2026-02-07 at 10 57 21 AM" src="https://github.com/user-attachments/assets/18c4d56d-482e-4042-8cbd-f8fe2cbbbe51" />

<img width="677" height="638" alt="Screenshot 2026-02-13 at 8 26 48 AM" src="https://github.com/user-attachments/assets/ac486b4a-d555-4df0-bb08-0d63469b16ff" />


The firmware for the ESP WT32-ETH01 can be found in this repository and can easily be adapted to other ESPs.

To connect to the aforementioned Froeling SP Dual, a TTL to RS232 converter is needed; I have chosen the Waveshare Rail-Mount TTL To RS232 Galvanic Isolated Converter.

<img width="698" height="491" alt="Screenshot 2026-02-07 at 10 56 14 AM" src="https://github.com/user-attachments/assets/7e730be2-fc2a-40d4-a25d-f43063d35c0e" />

Additionally, the ESP's firmware can be extended with the ability to work independently from HA in a so called `Master` mode, to which it switches automatically if the connection to HA is interrupted, e.g., during a reboot. It then calculates the heating flow temperature according to the settings in its own web interface (in case heating was on when the connection got disrupted, heating continues for 20 minutes with the last set flow temperature) and starts and stops the heating according to its schedule ('#' ignores anything afterwards; '8-10' determines the heating period, and '@', if present, stands for the increased (or decreased in case of a negative value) flow temperature; this can be used when the delta between room temp and target temp is bigger, for example, in the morning)

<img width="653" height="807" alt="Screenshot 2026-02-13 at 8 28 01 AM" src="https://github.com/user-attachments/assets/3ecd87ce-e2d9-42af-9af1-ad816feae8c1" />

As can be seen in the screenshot, the first seven slots are for the heating schedule in Master mode (`ESP Status`), i.e., in case the ESP is disconnected from Home Assistant. `AppDaemon Status`, `ESP HA API Status`, and `ESP Modbus Status` show whether AppDaemon, Home Assistant, and the boiler are connected. `AppDaemon Status` is determined by the state of `input_boolean.appdaemon_running`, the logic of which can be found [here](https://github.com/franzbu/HomeAssistantHeating/blob/main/AppDaemon/appdaemon_watchdog.py).

`HK2 Enabled` signalls that heating circuit 2 is potentially activated; however, a value of not 0 in `HK2 Flow Target Temp (ESP)` activates heating, which is then reflected in `Heating On`.

`HK2 Flow Temp +10 (Master)` and `HK2 Flow Temp -10 (Master)` are used in `Master` mode to determine the flow temp, which is based on the boiler's outside temperature sensor, unless `Outside Temp`, which is based on a dallas temperature sensor connected to GPIO 54, is in place, then the latters's value is used. `Room Temp` is for an additional dallas temperature sensor, also connected to GPIO 54 (and distinguished by its address -> both need to be changed to the ones of the dallas sensors used).

`Time (Manual Override)`, as already mentioned, allows for the manual adjustment of date and time in case of missing internet connection.

One of the reasons for using an ESP is Froeling having made it possible to write the target flow temperature into the RAM of the boiler, avoiding having to write to EEPROM registers, the lifetime of which is limited. However, this register (48001-48018 for Froeling's 18 heating circuits) needs to be updated within two minutes, otherwise heating stops, and the ESP automatically takes care of that - as long as the value in `input_number.target_flow_temp` is not 0, the ESP keeps poking the boiler.

Other than that, the ESP makes the boiler smart in the sense that its entities can be directly integrated into Home Assistant via ESPHome (already integrated into HA, so all entities the ESP is set up for are instantaneously writable and/or readable in HA). However, if that is the only thing one wants, then [GyroGearl00se's HA integration](https://github.com/GyroGearl00se/ha_froeling_lambdatronic_modbus) might be the preferrable option.

In this repo there is also a firmware file for the Waveshare ESP32-P4-NANO; compiling requires ESPHome 2026.2.0 or newer.

<img width="319" height="329" alt="Screenshot 2026-02-13 at 8 20 30 AM" src="https://github.com/user-attachments/assets/29b461ea-b1f1-4f5a-834e-1a129d0c9ae3" />


<img width="509" height="409" alt="Screenshot 2026-02-13 at 8 23 19 AM" src="https://github.com/user-attachments/assets/b3757574-4caf-4d44-88d6-aee97cdbc305" />


Below you can see a comparison between the two boards:

<img width="601" height="370" alt="Screenshot 2026-02-13 at 8 22 33 AM" src="https://github.com/user-attachments/assets/f2ddd4d1-315d-4c23-8830-8878a39c7a49" />

The firmware in the two examples forwards a range of entities from Froeling to HA; they can easily be changed or extended by consulting [Froeling's Modbus documentation]([https://github.com/GyroGearl00se/ha_froeling_lambdatronic_modbus](https://github.com/franzbu/HomeAssistantHeating/blob/main/B1200522_ModBus%20Lambdatronic%203200_50-04_05-19_de.pdf))

The ESP directly listens to `input_number.target_flow_temp` and starts and stops heating while also setting the flow temperature. The optional class 
[FroelingHeatingESP](https://github.com/franzbu/HomeAssistantHeating/blob/main/AppDaemon/heating_froeling_esp.py) can act as watchdog for the ESP's health and send a warning in case of an issue.

---
