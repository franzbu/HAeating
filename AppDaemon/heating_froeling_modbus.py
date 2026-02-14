
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
    froeling_boiler_1_desired_temperature: 'number.froeling_boiler_1_desired_temperature'
    froeling_boiler_1_pump_control: 'sensor.froeling_boiler_1_pump_control'
    froeling_boiler_1_pump_on_off: 'binary_sensor.froeling_boiler_1_pump_on_off'
    froeling_boiler_1_recharge_when_temperature_is_below: 'number.froeling_boiler_1_recharge_when_temperature_is_below'
    froeling_boiler_1_top_temp: 'sensor.froeling_boiler_1_top_temperature'
    froeling_boiler_state: 'sensor.froeling_boiler_state'
    froeling_boiler_target_temperature: 'number.froeling_boiler_target_temperature'
    froeling_boiler_temp: 'sensor.froeling_boiler_temperature'
    froeling_buffer_1_charge_state: 'sensor.froeling_buffer_1_charge_state'
    froeling_buffer_1_pump_control: 'sensor.froeling_buffer_1_pump_control'
    froeling_buffer_1_pump_on_off: 'binary_sensor.froeling_buffer_1_pump_on_off'
    froeling_buffer_temp_1: 'sensor.froeling_buffer_1_top_temperature'
    froeling_buffer_temp_2: 'sensor.froeling_buffer_1_temperature_sensor_2'
    froeling_buffer_temp_3: 'sensor.froeling_buffer_1_temperature_sensor_3'
    froeling_buffer_temp_4: 'sensor.froeling_buffer_1_bottom_temperature'
    froeling_collector_flow_temp: 'sensor.froeling_collector_flow_temperature'
    froeling_collector_pump_control: 'sensor.froeling_collector_pump_control'
    froeling_collector_return_temp: 'sensor.froeling_collector_return_temperature'
    froeling_collector_shutdown_delta: 'number.froeling_collector_shutdown_difference'
    froeling_collector_startup_delta: 'number.froeling_collector_startup_difference'
    froeling_collector_temp: 'sensor.froeling_collector_temperature'
    froeling_current_control_of_the_collector_boiler_pump: 'sensor.froeling_current_control_of_the_collector_boiler_pump'
    froeling_exhaust_temp: 'sensor.froeling_exhaust_temperature'
    froeling_hk2_flow_actual_temp: 'sensor.froeling_hk2_flow_actual_temperature'
    froeling_hk2_flow_temp_external: 'number.froeling_hk2_flow_temperature_external_specification' #'number.froeling_hk2_flow_temp_external_specification'
    froeling_hk2_flow_temp_neg_10: 'number.froeling_hk2_flow_temperature_at_10degc_outside_temperature_2'
    froeling_hk2_flow_temp_pos_10: 'number.froeling_hk2_flow_temperature_at_10degc_outside_temperature'
    froeling_hk2_flow_temp_threshold_pump_off: 'number.froeling_hk2_heating_circuit_pump_off_when_flow_target_is_less_than'
    froeling_hk2_frost_protection_temperature: 'number.froeling_hk2_frost_protection_temperature'
    froeling_hk2_operating_mode: 'select.froeling_hk2_operating_mode'
    froeling_hk2_outside_temp_threshold_pump_on_in_heating_mode: 'number.froeling_hk2_outside_temperature_below_which_heating_circuit_pump_turns_on_in_heating_mode'
    froeling_hk2_outside_temperature_below_which_heating_circuit_pump_turns_on_in_setback_mode: 'number.froeling_hk2_outside_temperature_below_which_heating_circuit_pump_turns_on_in_setback_mode'
    froeling_hk2_pump_external: 'select.froeling_hk2_clearance_external_specification' #'select.hk2_clearance_external_specification'
    froeling_hk2_pump_on_off: 'binary_sensor.hk2_pump'
    froeling_hk2_reduction_of_flow_temperature_in_setback_mode: 'number.froeling_hk2_reduction_of_flow_temperature_in_setback_mode'
    froeling_hk2_temperature_at_buffer_top_where_overheat_protection_activates: 'number.froeling_hk2_temperature_at_buffer_top_where_overheat_protection_activates'
    froeling_induced_draft_control: 'sensor.froeling_induced_draft_control'
    froeling_induced_draft_speed: 'sensor.froeling_induced_draft_speed'
    froeling_max_buffer_temperature_below_when_solar_charging: 'number.froeling_maximum_buffer_temperature_below_when_solar_charging'
    froeling_operating_hours: 'sensor.froeling_operating_hours'
    froeling_operating_hours_in_fire_maintenance: 'sensor.froeling_operating_hours_in_fire_maintenance'
    froeling_outside_temperature: 'sensor.froeling_outside_temperature'
    froeling_oxygen_controller: 'sensor.froeling_oxygen_controller'
    froeling_primary_air: 'sensor.froeling_primary_air'
    froeling_remaining_heating_hours_until_ash_emptying_warning: 'sensor.froeling_remaining_heating_hours_until_ash_emptying_warning'
    froeling_residual_oxygen_content: 'sensor.froeling_residual_oxygen_content'
    froeling_return_sensor: 'sensor.froeling_return_sensor'
    froeling_solar_sensor_buffer_bottom: 'sensor.froeling_solar_sensor_buffer_bottom'
    froeling_solar_sensor_buffer_top: 'sensor.froeling_solar_sensor_buffer_top'
    froeling_system_state: 'sensor.froeling_system_state'

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
heating_pump_control:
  module: heating_automation
  class: HeatSupplyManager
  telegram_id: 79867494
  dependencies: # also used for list of rooms that are NOT standalone (only bad, wc, and bathroom are)
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

heating_froeling_modbus:
  module: heating_froeling_modbus
  class: FroelingHeatingModbus
  telegram_id: 79867494
  dependencies:
    - global_config
    - heating_pump_control

# Standard Rooms (Trigger the pump)
heating_stubbe:
  module: heating_automation
  class: RoomDemandCalculator
  solar_activation_temp: 20
  solar_peak_temp: 35
  dependencies: [global_config]

heating_blueroom:
  module: heating_automation
  class: RoomDemandCalculator
  solar_activation_temp: 20
  solar_peak_temp: 35
  dependencies: [global_config]

heating_kuche:
  module: heating_automation
  class: RoomDemandCalculator
  solar_activation_temp: 20
  solar_peak_temp: 35
  dependencies: [global_config]

heating_stibbile:
  module: heating_automation
  class: RoomDemandCalculator
  solar_activation_temp: 20
  solar_peak_temp: 35
  dependencies: [global_config]

heating_livingroom:
  module: heating_automation
  class: RoomDemandCalculator
  solar_activation_temp: 20
  solar_peak_temp: 35
  dependencies: [global_config]

heating_kitchen:
  module: heating_automation
  class: RoomDemandCalculator
  solar_activation_temp: 20
  solar_peak_temp: 35
  dependencies: [global_config]

heating_medroom:
  module: heating_automation
  class: RoomDemandCalculator
  solar_activation_temp: 20
  solar_peak_temp: 35
  dependencies: [global_config]

heating_bedroom:
  module: heating_automation
  class: RoomDemandCalculator
  solar_activation_temp: 20
  solar_peak_temp: 35
  dependencies: [global_config]

heating_hallway:
  module: heating_automation
  class: RoomDemandCalculator
  solar_activation_temp: 20
  solar_peak_temp: 35
  dependencies: [global_config]

heating_hof:
  module: heating_automation
  class: RoomDemandCalculator
  solar_activation_temp: 20
  solar_peak_temp: 35
  dependencies: [global_config]

heating_gang:
  module: heating_automation
  class: RoomDemandCalculator
  solar_activation_temp: 20
  solar_peak_temp: 35
  dependencies: [global_config]

# Standalone Rooms (no pump trigger)
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
# FROELING HEATING MODBUS (Actual Boiler Interaction)
# ==================================================================================================
class FroelingHeatingModbus(hass.Hass):
    def initialize(self):
        self.gl = self.get_app("global_config")
        
        self.flow_temp_entity = self.gl.get_heating('froeling_hk2_flow_temp_external')      
        self.pump_enable_entity = self.gl.get_heating('froeling_hk2_pump_external')         
        self.main_mode_entity = self.gl.get_heating('froeling_hk2_operating_mode')             
        
        self.flow_target_helper = "input_number.target_flow_temp"
        self.telegram_target = self.args.get('telegram_id') 

        self.last_flow_write_time = self.get_now()

        if not self.check_system_health():
            return

        self.log("Modbus Interface Healthy. Registering listeners.")
        
        self.listen_state(self.on_target_flow_change, self.flow_target_helper)
        self.listen_state(self.enforce_automatik_mode, self.main_mode_entity)
        
        # Start the Keep-Alive heartbeat (runs every 110s)
        self.run_every(self.modbus_keep_alive, self.get_now(), 110)
        
        # Run an initial evaluation right away
        self.evaluate_and_write_modbus()

    def check_system_health(self):
        critical_entities = [
            self.flow_temp_entity,
            self.pump_enable_entity,
            self.main_mode_entity,
            self.flow_target_helper
        ]
        
        missing = []
        unavailable = []
        
        for entity in critical_entities:
            if not self.entity_exists(entity):
                missing.append(entity)
                continue
            
            state = self.get_state(entity)
            
            # Allow 'unknown' for main_mode_entity as it happens during active heating
            if entity == self.main_mode_entity and state == "unknown":
                continue

            if state in ["unavailable", "unknown", None]:
                unavailable.append(f"{entity} ({state})")

        if missing:
            self.log(f"CRITICAL: Entities missing: {missing}", level="ERROR")
            return False

        if unavailable:
            self.log(f"Startup delayed. Waiting for: {unavailable}", level="WARNING")
            self.run_in(self.initialize, 30)
            return False
        
        return True

    def on_target_flow_change(self, entity, attribute, old, new, args):
        # Instantly react to a change in the target flow helper
        self.evaluate_and_write_modbus()

    def modbus_keep_alive(self, kwargs):
        # The heartbeat function
        self.evaluate_and_write_modbus()

    def evaluate_and_write_modbus(self):
        try:
            target = float(self.get_state(self.flow_target_helper) or 0.0)
        except (ValueError, TypeError):
            target = 0.0

        if target > 0:
            # 1. Continually write Flow Temp (Triggering Boiler Keep-Alive)
            self.call_service("number/set_value", entity_id=self.flow_temp_entity, value=target)
            self.last_flow_write_time = self.get_now()

            # 2. Ensure External Pump is Enabled ('ein')
            current_pump_state = self.get_state(self.pump_enable_entity)
            if current_pump_state != 'ein':
                self.log(f"Enabling Heating Pump (State was: {current_pump_state})")
                self.call_service("select/select_option", entity_id=self.pump_enable_entity, option='ein')
                if self.telegram_target:
                     self.notify(self.telegram_target, "🌀 Heating Active", f"Pump enabled.\nFlow Target: {target}°C", True)
        else:
            # Target is 0. Do NOT write 0 to the boiler Modbus register. 
            # Simply stop poking it.
            pass

    def enforce_automatik_mode(self, entity, attribute, old, new, args):
        if new in ["automatik", "unknown", "unavailable", None]:
            return

        time_since_last_write = (self.get_now() - self.last_flow_write_time).total_seconds()
        
        if time_since_last_write < 130:
            return

        self.log(f"Heating idle (last write {int(time_since_last_write)}s ago). Mode is '{new}'. Resetting to 'automatik'.")
        self.call_service("select/select_option", entity_id=entity, option='automatik')

    def notify(self, target, title, message, disable_notification=True):
        self.gl.send_telegram(target, title, message, disable_notification)