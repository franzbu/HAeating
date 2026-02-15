
''' Manual
FroelingHeatingESP class is a watchdog and notification system.

Its entire existence is waiting for binary_sensor.froeling_modbus_status to change so 
it can fire off a Telegram message.

HeatSupplyManager does all the heavy lifting for the mathematical logic, the physical ESP32 handles 
all of the hardware-level fail-safes, and this AppDaemon class just sits in the background 
keeping an eye on the communication health.

'''

''' apps.yaml
# ==========================================
# GLOBAL CONFIGURATION
# ==========================================
global_config:
  module: globals
  class: GlobalSettings
  temp_room_map:
    stubbe: 'sensor.wall_thermostat_with_switching_output_for_brand_switches_stubbe_temperature'
    blueroom: 'sensor.temperature_and_humidity_sensor_blue_room_temperature'
    kuche: 'sensor.wall_thermostat_with_switching_output_for_brand_switches_kuche_temperature'
    stibbile: 'sensor.wall_thermostat_with_switching_output_for_brand_switches_stibbile_temperature'
    livingroom: 'sensor.temperature_and_humidity_sensor_living_room_temperature'
    kitchen: 'sensor.wall_thermostat_with_switching_output_for_brand_switches_kitchen_temperature'
    medroom: 'sensor.wall_thermostat_with_switching_output_for_brand_switches_med_temperature'
    bedroom: 'sensor.temperature_and_humidity_sensor_bedroom_temperature'
    hallway: 'sensor.temperature_and_humidity_sensor_hallway_temperature'
    hof: 'sensor.wall_thermostat_with_switching_output_for_brand_switches_hof_temperature'
    gang: 'sensor.temperature_and_humidity_sensor_gang_mama_temperature'
    bad: 'sensor.radiator_thermostat_evo_bad_temperature'
    wc: 'sensor.radiator_thermostat_evo_wc_temperature'
    bathroom: 'sensor.radiator_thermostat_evo_bathroom_temperature'
  
  heating_map:
    froeling_boiler_1_desired_temperature: 'number.froeling_boiler_target_temp'
    froeling_boiler_1_pump_control: 'sensor.froeling_boiler_pump_control'
    froeling_boiler_1_pump_on_off: 'binary_sensor.froeling_boiler_pump_status' 
    froeling_boiler_1_top_temp: 'sensor.froeling_boiler_temp_top'
    froeling_boiler_state: 'sensor.froeling_boiler_state'
    froeling_boiler_target_temperature: 'number.froeling_boiler_target_temp'
    froeling_boiler_temp: 'sensor.froeling_boiler_temp'
    froeling_buffer_1_charge_state: 'sensor.froeling_buffer_charge_state'
    froeling_buffer_1_pump_control: 'sensor.froeling_buffer_pump_control'
    froeling_buffer_1_pump_on_off: 'binary_sensor.froeling_buffer_pump_on_off' 
    froeling_buffer_temp_1: 'sensor.froeling_buffer_temp_sensor_1'
    froeling_buffer_temp_2: 'sensor.froeling_buffer_temp_sensor_2'
    froeling_buffer_temp_3: 'sensor.froeling_buffer_temp_sensor_3'
    froeling_buffer_temp_4: 'sensor.froeling_buffer_temp_sensor_4'
    froeling_collector_flow_temp: 'sensor.froeling_collector_flow_temp'
    froeling_collector_pump_control: 'sensor.froeling_collector_pump_control'
    froeling_collector_return_temp: 'sensor.froeling_collector_return_temp'
    froeling_collector_shutdown_delta: 'number.froeling_collector_shutdown_difference'
    froeling_collector_startup_delta: 'number.froeling_collector_startup_difference'
    froeling_collector_temp: 'sensor.froeling_collector_temp'
    froeling_current_control_of_the_collector_boiler_pump: 'sensor.froeling_collector_boiler_pump_control'
    froeling_exhaust_temp: 'sensor.froeling_boiler_flue_gas_temp'
    froeling_hk2_flow_actual_temp: 'sensor.froeling_hk2_flow_actual_temp'
    froeling_hk2_flow_target_temp: 'sensor.froeling_hk2_flow_target_temp'
    froeling_hk2_flow_temp_external: 'number.froeling_hk2_flow_setpoint_external'
    froeling_hk2_flow_temp_threshold_pump_off: 'number.froeling_hk2_heating_circuit_pump_off_when_flow_target_is_less_than'
    froeling_hk2_frost_protection_temperature: 'number.froeling_hk2_frost_protection_temp'
    froeling_hk2_operating_mode: 'select.froeling_hk2_operating_mode'
    froeling_hk2_pump_external: 'select.froeling_hk2_clearance_external_specification'
    froeling_hk2_pump_on_off: 'binary_sensor.froeling_hk2_pump_status' 
    froeling_induced_draft_control: 'sensor.froeling_boiler_induced_draught_control'
    froeling_induced_draft_speed: 'sensor.froeling_boiler_induced_draught_speed'
    froeling_outside_temperature: 'sensor.froeling_boiler_outside_temp'
    froeling_oxygen_controller: 'sensor.froeling_boiler_oxygen_controller'
    froeling_primary_air: 'sensor.froeling_boiler_primary_air'
    froeling_remaining_heating_hours_until_ash_emptying_warning: 'sensor.froeling_boiler_remaining_heating_hours_until_ash_emptying_warning'
    froeling_residual_oxygen_content: 'sensor.froeling_boiler_residual_oxygen_content'
    froeling_return_sensor: 'sensor.froeling_boiler_return_sensor'
    froeling_system_state: 'sensor.froeling_boiler_system_state'

  temp_outdoor_map:
    outdoor_temp: 'sensor.temperature_and_humidity_sensor_outdoor_balkon_temperature'
    garten_temp: 'sensor.temperature_and_humidity_sensor_outdoor_garten_temperature'

  energy_map:
    main_meter: 'sensor.goe_904101_cec_0_0'
    ev_charger: 'sensor.goe_240930_eto'
    tesla_added: 'sensor.tesla_energy_added'

  car_map:
    tracker: 'device_tracker.tesla_location_tracker'
    charger_plugged: 'binary_sensor.goe_240930_car_0'

  garage_map:
    door_state: 'binary_sensor.shelly1minig3_543204694e60_input_0_input'
    door_switch: 'input_boolean.garage_door'
    relay: 'switch.shelly1minig3_543204694e60_switch_0'
    autoclose_toggle: 'input_boolean.garage_autoclose'

  lock_map:
    nuki_lock: 'lock.smart_lock_ultra'
    lock_switch: 'input_boolean.front_door'

  system_map:
    last_update_tracker: 'input_text.goecontroller_last_update'
    regular_shutdown: 'input_boolean.regular_shutdown'
    appdaemon_running: 'input_boolean.appdaemon_running'

  valve_map:
    valve_stubbe: 'sensor.heating_circuit_5_stubbe_valve_position'
    valve_blueroom: 'sensor.heating_circuit_11_blueroom_valve_position'
    valve_stibbile: 'sensor.heating_circuit_1_stibbile_valve_position'
    valve_kuche: 'sensor.heating_circuit_7_kuche_valve_position'
    valve_bedroom: 'sensor.heating_circuit_3_bedroom_valve_position'
    valve_medroom: 'sensor.heating_circuit_4_med_valve_position'
    valve_livingroom: 'sensor.heating_circuit_9_living_room_valve_position'
    valve_kitchen: 'sensor.heating_circuit_12_kitchen_valve_position'
    valve_hallway: 'sensor.heating_circuit_9_hallway_valve_position'
    valve_gang: 'sensor.heating_circuit_11_gang_valve_position'
    valve_hof: 'sensor.heating_circuit_5_hof_ost_valve_position'


# ==========================================
# HEATING SYSTEM APPS
# ==========================================

# Master Supply Manager: Calculates target flow based on claims
heating_pump_control:
  module: heating_automation
  class: HeatSupplyManager
  telegram_id: 79867494
  dependencies:
    - global_config
    - heating_stubbe
    - heating_blueroom
    - heating_kuche
    - heating_stibbile
    - heating_livingroom
    - heating_kitchen
    - heating_medroom
    - heating_bedroom
    - heating_hallway
    - heating_hof
    - heating_gang

# Boiler Interface: Forwards calculation to physical hardware
froeling_interface:
  module: heating_froeling_esp
  class: FroelingHeatingESP
  telegram_id: 79867494
  dependencies:
    - global_config
    - heating_pump_control

# --- Standard Rooms (Trigger the pump) ---
heating_stubbe:
  module: heating_automation
  class: RoomDemandCalculator
  dependencies: [global_config]
  solar_activation_temp: 20
  solar_peak_temp: 35

heating_blueroom:
  module: heating_automation
  class: RoomDemandCalculator
  dependencies: [global_config]

heating_kuche:
  module: heating_automation
  class: RoomDemandCalculator
  dependencies: [global_config]

heating_stibbile:
  module: heating_automation
  class: RoomDemandCalculator
  dependencies: [global_config]

heating_livingroom:
  module: heating_automation
  class: RoomDemandCalculator
  dependencies: [global_config]

heating_kitchen:
  module: heating_automation
  class: RoomDemandCalculator
  dependencies: [global_config]

heating_medroom:
  module: heating_automation
  class: RoomDemandCalculator
  dependencies: [global_config]

heating_bedroom:
  module: heating_automation
  class: RoomDemandCalculator
  dependencies: [global_config]

heating_hallway:
  module: heating_automation
  class: RoomDemandCalculator
  dependencies: [global_config]

heating_hof:
  module: heating_automation
  class: RoomDemandCalculator
  dependencies: [global_config]

heating_gang:
  module: heating_automation
  class: RoomDemandCalculator
  dependencies: [global_config]

# --- Standalone Rooms (no pump trigger) ---
heating_bad:
  module: heating_automation
  class: RoomDemandCalculator
  dependencies: [global_config]

heating_wc:
  module: heating_automation
  class: RoomDemandCalculator
  dependencies: [global_config]

heating_bathroom:
  module: heating_automation
  class: RoomDemandCalculator
  dependencies: [global_config]

'''

import hassapi as hass  # type: ignore
from datetime import datetime, timedelta, time

# ==================================================================================================
# FROELING HEATING ESP INTERFACE
# ==================================================================================================
class FroelingHeatingESP(hass.Hass):
    def initialize(self):
        self.gl = self.get_app("global_config")
        self.telegram_target = self.args.get('telegram_id')
        self.target_temp_helper = "input_number.target_flow_temp"
        self.modbus_sensor = "binary_sensor.froeling_modbus_status"
        
        self.startup_timer = None
        self.try_startup()

    def try_startup(self, kwargs=None):
        if not self.check_system_health():
            self.startup_timer = self.run_in(self.try_startup, 30)
            return
        self.boot_up()

    def check_system_health(self):
        # Only block on the presence of the main target helper now
        if not self.entity_exists(self.target_temp_helper) or self.get_state(self.target_temp_helper) in ["unavailable", "unknown", None]:
            self.log(f"Waiting for {self.target_temp_helper}...", level="WARNING")
            return False
        return True

    def boot_up(self):
        self.log("Froeling ESP Interface Booted. Modbus watchdog active.")
        
        # Monitor Modbus health (always active regardless of initial state)
        self.listen_state(self.on_modbus_status_change, self.modbus_sensor)
        
        # Initial check in case it's already down at boot
        if self.get_state(self.modbus_sensor) == "off":
            self.on_modbus_status_change(self.modbus_sensor, None, None, "off", None)

    def on_modbus_status_change(self, entity, attribute, old, new, args):
        if new == "off":
            self.log("MODBUS DISCONNECTED!", level="ERROR")
            if self.telegram_target:
                self.notify(self.telegram_target, "🚨 Boiler Modbus Down", 
                            "ESP32 lost link to boiler.", True)
        elif new == "on" and old == "off":
            self.log("MODBUS RESTORED", level="INFO")
            if self.telegram_target:
                self.notify(self.telegram_target, "✅ Boiler Modbus Restored", 
                            "Modbus connection established.", True)

    def notify(self, target, title, message, disable_notification=True):
        self.gl.send_telegram(target, title, message, disable_notification)
