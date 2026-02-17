


# Home Assistant Heating

First things first: let me show you what your heating automation can look like:

<img width="737" height="801" alt="Screenshot 2026-02-17 at 8 32 36 AM" src="https://github.com/user-attachments/assets/9d5c47bb-1a20-4efe-a4a7-a5b65a6dd1ea" />

This is a screenshot of a possible HA dashboard with two example rooms (the four sections with the diagrams are hardware-specific and might and probably will look entirely different on your dashboard). 

Below you see a dark-mode one:

<img width="924" height="532" alt="Screenshot 2026-02-17 at 8 04 22 AM" src="https://github.com/user-attachments/assets/32b9a76a-f5c5-4db7-a06a-e69e7604f3b8" />



If heating is set to `Off` (top left), it stays off; if it is set to `Party`, it stays on. However, it is the two options in between, `Auto` and `Heating`, where the magic happens.

The one goal of this heating automation has been 'set up and forget'. The house ideally just heats itself to the desired temperature, taking into consideration premeditated factors such as personal circumstances (work, holiday at home, gone), purpose of room, day of week, time of day, or time of year. Even factors such as the current sun exposure can play a role and can optionally be taken into consideratoin by this heating automation.

The present heating automation works regardless of which kind of heating system is in place; it is divided into three abstraction layers: (1) and (2) need not to be touched, as they calculate the heating demand and the required flow temperature of the heating 'fluid'; (3) links the automation to the hardware in place and will be in need of adjusting (unless you happen to own a Froeling Lambdatronic-powered boiler such as the SP Dual, then you can choose from two examples provided farther down). Linking your heating hardware, however, boils down to accessing one variable only, which can be done in various ways such as a HA automation or an ESP.

This heating control system has been built with **AppDaemon** (Python) for **Home Assistant**. Why AppDaemon, you may ask. Well, AppDaemon has is unparalleled when it comes to using Python within Home Assistant without restrictions, including the possibility of creating instances of classes (which, for example, PyScript cannot do). The availability of all Python libraries and possibilities allows for the ultimate straightforwardness and efficiency. 

## 🛠 System Architecture
The heating automation is split into three specialized layers; the first two are abstraction layers that can stay the same for any kind of heating there is. Layer 3 is all about how to address the existing heating hardware and will have to adjusted - two examples are given.

(1) **Layer 1: Room Level:** RoomDemandCalculator: (The Brain):** An instance of this app runs for every room. It handles schedules, hysteresis, solar gain compensation, boost demands, and calculates the heat claim for the room.
  
(2) **Layer 2: Central Heating Control:** HeatSupplyManager: (The Muscle):** HeatSupplyManager acts as control center for juggling the heating demands for all rooms. Heating is initiated by writing the target flow temperature to the HA Helper `input_number.target_flow_temp` (heating stops by writing 0).
  
(3) **Layer 3: Hardware Interface:** Connects to the actual hardware (e.g., Froeling SP Dual): The hardware interface listens to `input_number.target_flow_temp` and initiates heating in accordance with the value in `input_number.target_flow_temp`. 

---

### AppDaemon `apps.yaml` Example
```yaml
heating_livingroom:
  module: heating_automation
  class: RoomDemandCalculator
  dependencies: [global_config]

heating_pump_control:
  module: heating_pump_control
  class: HeatSupplyManager
  dependencies:
    - global_config
    - heating_livingroom
    - heating_bedroom
  telegram_id: "-1001234536788"
```

The AppDaemon code relies on a `global_config:` section in [apps.yaml](https://github.com/franzbu/HomeAssistantHeating/blob/main/AppDaemon/apps.yaml) and the module [globals.py](https://github.com/franzbu/HomeAssistantHeating/blob/main/AppDaemon/globals.py).

In case you are wondering what the listing of the valve states is for, this is done to prevent the heating circuit pump pushing against closed valves; in case they are all closed (< 20%), heating stops.

Rooms that are only heated passively, i.e., they will never have the heating started but simply benefit from the heating up and running, are not listed in the `dependencies:` section of `heating_pump_control:`. The same, for example, goes for radiators that are heated by gravitational flow (simpy physics instead of circuit pump).

---

AppDaemon gets the room names and the names of the HA Helpers based on this config, and for that it is important that the Helpers are created following the naming pattern in the section below.

### Required Home Assistant Entities

Helpers to create for each room, replace 'stubbe' with the name of each of the rooms:
```
schedule.standard_stubbe
schedule.holiday_stubbe
schedule.party_stubbe
schedule.temp_stubbe
schedule.off_stubbe

input_select.heating_schedule_stubbe: Standard, Holiday, Party, Temporary, Off
input_select.heating_claim_stubbe

input_number.target_temp_stubbe: 5-30 (0.5 steps)
input_number.delta_temp_stubbe: 1-5 (0.5 steps) when
input_number.base_temp_stubbe: 5-30 (0.5 steps): this is the temp target_temp is set to outside of heating periods
input_number.heat_temp_stubbe: 5-30 (0.5 steps): this is the temp target_temp is set to throughout heating periods (if now overwritten by ‘temp’ in a schedule’s attribute of that specific heating period)

input_text.next_event_stubbe: for showing schedule’s attribute ‘next_event’ on dashboard

optional and only for rooms with sun compensation: input_number.sun_compensation_stubbe: 1-5 (1 steps)
```

helpers to create once for heating automation as a whole:
```
input_boolean.heating_automation
input_number.heating_boost_threshold (2-25)
input_number.heating_baseline_0_deg (25-45)
input_number.heating_boost_factor (0.5-4)
input_number.heating_claim_duration (0-60)
input_number.heating_margin (0-1)
input_number.max_flow_temp (30-50)
input_number.flow_temp_multi_room_offset (0-1; step: 0.1)
input_number.hk2_target_flow_temp
```

---

## Layer 1: Room-Level Logic (`RoomDemandCalculator`)

Each room functions as an independent agent. It monitors its own temperature and decides whether to "request" heat from the boiler.


---

### Individual Room Settings

Each room is managed via dedicated dashboard section containing the following data points:

#### Standard View

<img width="385" height="112" alt="Screenshot 2026-02-07 at 10 35 32 AM" src="https://github.com/user-attachments/assets/0c0b9c39-e116-45f0-83b4-16c06f6ccf9b" />

* **Live Metrics:** Current temperature, heating valve opening percentage, and humidity.
* **Target temp:** Current heating target temperature and the name of the currently active schedule.
* **Event Info:** Swipe horizontally to view detailed information regarding the current or next heating event.
* **Advanced:** Switching between the five different schedules (Standard, Holiday, Party, Temporary, Off) can, besides the general way of swiping and long-tapping/pressing the desired schedult - short-tap/press leads to editing) be achieved via 'shortcut' by long-tapping/pressing the schedule's icon (Standard), remaining button (Off), temperature (Holiday), valve state (Party), and humidity (Temporary). 

Swiping the upper section leads to further settings and information:

| Swiping upper secgtion |
| :--- |
| <img width="292" src="https://github.com/user-attachments/assets/6e5e54fc-775d-4a4b-8153-d598174724bc" /> |
| <img width="294" src="https://github.com/user-attachments/assets/58a7a374-33ea-4a6c-8f62-0d0614033cf7" /> |
| <img width="302" src="https://github.com/user-attachments/assets/338cac9c-323b-415f-a72d-5ae0efd3a939" /> |


* **Boost:** Toggles and displays Boost - more farther down.

* **Sun compensation:** If a room experiences solar gain, the target temperature can temporarily be decreased - more farther down.
  

#### Additional Parameters

* **Heating Delta ($\Delta$):** The "Start" trigger. Heating turns on when the temperature drops below `Target Temp - Delta`.
    * *Control:* Tap the card/icon to adjust; long-tap for larger increments.
<img width="407" height="113" alt="Screenshot 2026-02-07 at 10 37 04 AM" src="https://github.com/user-attachments/assets/4fd796f9-9c4a-43ab-8d84-e34d37a3c926" />



* **Base Temp:** The "Background" temperature used outside of scheduled heating events. This allows for passive heating to prevent the room from getting too cold.
<img width="375" height="105" alt="Screenshot 2026-02-07 at 10 37 27 AM" src="https://github.com/user-attachments/assets/3b2c6b25-d1bf-4f1d-b902-28566b1f9d08" />


* **Heat Temp:** The default target temperature used during active schedule events if no specific temperature is defined within the schedule itself.
<img width="377" height="97" alt="Screenshot 2026-02-07 at 10 37 49 AM" src="https://github.com/user-attachments/assets/f8f194f5-165b-42b0-a338-0a6951cd8fb9" />


The yaml file for the dashboard for an example room can be seen [here](https://github.com/franzbu/HomeAssistantHeating/blob/main/dashboard/dashboard_room.yaml); for its full functionality (long-tap/press on icons and buttons increases/decreases step size), [these HA scripts](https://github.com/franzbu/HomeAssistantHeating/tree/main/HA) can be put in place.

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


### ☀️ Solar Compensation
If a room has high solar gain (e.g., south-facing windows), the automation proactively reduces the target temperature when it's warm outside. This is used as a means of compensating for the fact that with direct sun exposure the surrounding temperature can be lowered to achieve the same comport level.

The most straightforward solution to gauge the sun's intensity is a brightness sensor; however momentary cloudiness would need to be taken into account. What I have found a reliable source of gauging the sun's intensity is the temperature in a greenhouse, and since there is one in my garden, that is what I use.

#### How the Calculation Works
The logic uses the range between 20.0°C (start) and 35.0°C (peak) to decide how much of that 1–5 degree "discount" to apply:
Below 20°C Garden Temp: The offset is 0.0. The room stays at the full target temp. At 35°C Garden Temp: The offset is 100% of the helper value. If the helper is set to 3.0, the target temp drops by 3.0°C. In between (e.g., 27.5°C): The offset is scaled linearly (at 27.5°C, it would be 50% of the helper).


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

### Climate Entity

Rather than using the pre-set climate device, this heating automation uses an input_number per room for setting the target temperature. Since thermostats still rely on HA's climate devices, each input_number is synced to its climate device and vice versa in case the target temperature is changed on, for example, the native thermostat app. This two-way sync has been done using HA's automation, an example can be seen [here](https://github.com/franzbu/HomeAssistantHeating/blob/main/HA/climate_sync_select_bedroom.yaml).


---

## Layer 2: Central Control (`HeatSupplyManager`)

The central controller monitors all rooms; if at least one room is claiming heat, heating is initiated; however, this automatic heating is only enabled if `input_select.heating_mode` is not `Off` (heating stays off regardless of any room's heating claims) and not `Party' (heating stays on)


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

### Dynamic Flow Temperature (Heating Curve)
The system doesn't use a fixed water temperature. It calculates the **Flow Target** using a linear heating curve:

$$T_{flow} = (-Adjustment \times T_{outdoor}) + Baseline_{0^\circ C} + Boost_{max} + Offset_{multi}$$

* **Baseline:** The required flow temperature when it is $0^\circ C$ outside.
* **Adjustment:** The "slope" of the curve.
* **Multi-room Offset:** For every additional room asking for heat, the flow temperature is nudged higher to account for increased thermal load.


`HeatSupplyManager` is responsible for calculating the base flow temperature depending on the outside temperature primarily, and the amount of rooms to heat secondarily (the latter is optional and can be activated via dashboard).

The outside temperature sensor can have one or more backup sensors, just in case your friendly squirrel chews through the Dallas DS18B20 temperature sensor cable or the battery runs out of your Homematic outdoor temperature sensor.

In apps.yaml, section `temp_outdoor_map:`, any number of outdoor sensors can be listed with descending priority (first is used first). The list is dynamic, i.e., should a sensor with a higher priority start delivering valid data, AppDaemon is picking that up and switching back.

---
## Layer 3: Connection to Heating Hardware

The principle is simple: HA's helper `input_number.target_flow_temp` signals heating demand when it contains the required flow temperature; it signals no heating demand if it is set to `0`. This respository contains two examples how this can be used to connect the actual heating device, which can be a thermal heat pump, wood boiler, ... 

### (A) Froeling wood boiler, using [ha_froeling_lambdatronic_modbus](https://github.com/GyroGearl00se/ha_froeling_lambdatronic_modbus).

The example can be seen [here](https://github.com/franzbu/HomeAssistantHeating/blob/main/AppDaemon/heating_froeling_modbus.py).

---

### (B) Froeling wood boiler, using an ESP32

The ESP is programmed to listen to changes to HA's input_number.target_flow_temp and starts (when value is set to the required flow temp) and stops (when value is set to 0) heating accordingly. The ESP is connected to HA via ethernet (also Wifi or other wireless communication will work; however, ethernet is recommended for its reliability) and to the Froeling boiler via Modbus.


<p float="left">
  <img src="https://github.com/user-attachments/assets/18c4d56d-482e-4042-8cbd-f8fe2cbbbe51" height="300" />
  <img src="https://github.com/user-attachments/assets/ac486b4a-d555-4df0-bb08-0d63469b16ff" height="300" />
</p>

The firmware for the ESP WT32-ETH01 can be found in this repository and can easily be adapted to other ESPs.

To connect to the aforementioned Froeling SP Dual, a TTL to RS232 converter is needed; I have chosen the Waveshare Rail-Mount TTL To RS232 Galvanic Isolated Converter.

<p float="left">
  <img src="https://github.com/user-attachments/assets/7e730be2-fc2a-40d4-a25d-f43063d35c0e" height="300" />
</p>

Additionally, the ESP's firmware can be extended with the ability to work independently from HA in a so called `Master` mode, to which it switches automatically if the connection to HA is interrupted, e.g., during a reboot. It then calculates the heating flow temperature according to the settings in its own web interface (in case heating was on when the connection got disrupted, heating continues for 20 minutes with the last set flow temperature) and starts and stops the heating according to its schedule ('#' ignores anything afterwards; '8-10' determines the heating period, and '@', if present, stands for the increased (or decreased in case of a negative value) flow temperature; this can be used when the delta between room temp and target temp is bigger, for example, in the morning)

<img width="622" height="882" alt="Screenshot 2026-02-16 at 11 41 33 AM" src="https://github.com/user-attachments/assets/edfd262e-ddd3-4d51-8b6a-a1eb00d2acb4" />


As can be seen, the first seven slots are for the heating schedule in Master mode (`ESP Status`), i.e., in case the ESP is disconnected from Home Assistant. 

`AppDaemon Status`, `ESP HA API Status`, and `ESP Modbus Status` show whether AppDaemon, Home Assistant, and the boiler are connected. `AppDaemon Status` is determined by the state of `input_boolean.appdaemon_running`, the logic of which can be found [here](https://github.com/franzbu/HomeAssistantHeating/blob/main/AppDaemon/appdaemon_watchdog.py).

`HK2 Enabled` signals that heating circuit 2 is potentially activated; however, a value of not 0 in `HK2 Flow Target Temp (ESP)` activates heating, which is then reflected in `Heating On`.

`HK2 Flow Temp +10 (Master)` and `HK2 Flow Temp -10 (Master)` are used in `Master` mode to determine the flow temp, which is based on the boiler's outside temperature sensor, unless `Outside Temp`, which is based on a Dallas temperature sensor connected to GPIO 54, is in place, then the latters's value is used. `Room Temp` is for an additional dallas temperature sensor, also connected to GPIO 54 (and distinguished by its address -> both need to be changed to the ones of the dallas sensors used).

`Time (Manual Override)`, as already mentioned, allows for the manual adjustment of date and time in case of missing internet connection.

Additionally, there are five temperature senors (Dallas DS18B20) connected through 'one_wire' for outside temperature, room temperature and additional heating and solar flow temperatures.

---

One of the reasons for using an ESP is the ability to write the target flow temperature into the RAM of the boiler, avoiding having to write to EEPROM registers, the lifetime of which is limited. However, this register (48001-48018 for Froeling's 18 heating circuits) needs to be updated within two minutes, otherwise heating stops, and the ESP automatically takes care of that - as long as the value in `input_number.target_flow_temp` is not 0, the ESP keeps poking the boiler (this 'poking' can also be done by Home Assistant when using the integration in (A); however, using an ESP is the straightforward option).

Other than that, the ESP makes the boiler smart in the sense that its entities can be directly integrated into Home Assistant via ESPHome (already integrated into HA, so all entities the ESP is set up for are instantaneously writable and/or readable in HA). However, if that is the only thing one wants, then [GyroGearl00se's HA integration](https://github.com/GyroGearl00se/ha_froeling_lambdatronic_modbus) might be the preferrable option.

In this repo there is also a firmware file for the Waveshare ESP32-P4-NANO, and while the WT32-ETH01 will do just fine the ESP32-P4-NANO is the fast and future-proof option for those who might extend the project at a future stage with, let's say, a touchscreen.

<p float="left">
  <img src="https://github.com/user-attachments/assets/29b461ea-b1f1-4f5a-834e-1a129d0c9ae3" height="300" />
  <img src="https://github.com/user-attachments/assets/b3757574-4caf-4d44-88d6-aee97cdbc305" height="300" />
</p>

The ESP forwards select entities from Froeling to HA; they can easily be [changed or extended](https://github.com/franzbu/HomeAssistantHeating/blob/main/doc/B1200522_ModBus%20Lambdatronic%203200_50-04_05-19_de.pdf).

The ESP directly listens to `input_number.target_flow_temp` and starts and stops heating while also setting the flow temperature. The optional class 
[FroelingHeatingESP](https://github.com/franzbu/HomeAssistantHeating/blob/main/AppDaemon/heating_froeling_esp.py) can act as watchdog for the ESP's health and send a warning in case of an issue.

---
