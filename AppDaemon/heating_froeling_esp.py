
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

  temp_outdoor_map:
    dallas_outdoor_temp: 'sensor.froeling_temp_outside'
    outdoor_temp: 'sensor.temperature_and_humidity_sensor_outdoor_balkon_temperature'
    froeling_outside_temperature: 'sensor.froeling_boiler_outside_temp'
    garten_temp: 'sensor.temperature_and_humidity_sensor_outdoor_garten_temperature'
  
  heating_map:
    froeling_boiler_1_pump_control: 'sensor.froeling_boiler_pump_control'
    froeling_boiler_1_pump_on_off: 'binary_sensor.froeling_boiler_pump_status' 
    froeling_boiler_state: 'sensor.froeling_boiler_state'
    froeling_boiler_temp: 'sensor.froeling_boiler_temp'
    froeling_buffer_1_charge_state: 'sensor.froeling_buffer_charge_state'
    froeling_buffer_1_pump_control: 'sensor.froeling_buffer_pump_control'
    froeling_buffer_temp_1: 'sensor.froeling_buffer_temp_sensor_1'
    froeling_buffer_temp_2: 'sensor.froeling_buffer_temp_sensor_2'
    froeling_buffer_temp_3: 'sensor.froeling_buffer_temp_sensor_3'
    froeling_buffer_temp_4: 'sensor.froeling_buffer_temp_sensor_4'
    froeling_collector_flow_temp: 'sensor.froeling_collector_flow_temp'
    froeling_collector_pump_control: 'sensor.froeling_collector_pump_control'
    froeling_collector_return_temp: 'sensor.froeling_collector_return_temp'
    froeling_collector_temp: 'sensor.froeling_collector_temp'
    froeling_current_control_of_the_collector_boiler_pump: 'sensor.froeling_collector_boiler_pump_control'
    froeling_exhaust_temp: 'sensor.froeling_boiler_flue_gas_temp'
    froeling_hk2_flow_actual_temp: 'sensor.froeling_hk2_flow_actual_temp'
    froeling_hk2_flow_target_temp: 'sensor.froeling_hk2_flow_target_temp'
    froeling_hk2_pump_external: 'select.froeling_hk2_enabled'
    froeling_hk2_pump_on_off: 'binary_sensor.froeling_hk2_pump_status' 
    froeling_induced_draft_control: 'sensor.froeling_boiler_induced_draught_control'
    froeling_induced_draft_speed: 'sensor.froeling_boiler_induced_draught_speed'
    froeling_oxygen_controller: 'sensor.froeling_boiler_oxygen_controller'
    froeling_primary_air: 'sensor.froeling_boiler_primary_air'
    froeling_residual_oxygen_content: 'sensor.froeling_boiler_residual_oxygen_content'
    froeling_return_sensor: 'sensor.froeling_boiler_return_sensor'
    froeling_system_state: 'sensor.froeling_boiler_system_state'
    froeling_hk2_flow_target_temp_external: 'sensor.froeling_hk2_flow_target_temp'

'''

import hassapi as hass  # type: ignore

# ==================================================================================================
# FROELING HEATING ESP INTERFACE
# ==================================================================================================
class FroelingHeatingESP(hass.Hass):
    def initialize(self):
        self.gl = self.get_app("global_config")
        self.telegram_target = self.args.get('telegram_id')
        self.target_temp_helper = "input_number.target_flow_temp"
        self.modbus_sensor = "binary_sensor.froeling_modbus_status"
        
        # Get the entity ID for the HK2 external pump control from globals
        self.hk2_pump_control = self.gl.get_heating("froeling_hk2_pump_external")
        
        self.startup_timer = None
        self.try_startup()

    def try_startup(self, kwargs=None):
        if not self.check_system_health():
            self.startup_timer = self.run_in(self.try_startup, 30)
            return
        self.boot_up()

    def check_system_health(self):
        if not self.entity_exists(self.target_temp_helper) or self.get_state(self.target_temp_helper) in ["unavailable", "unknown", None]:
            self.log(f"Waiting for {self.target_temp_helper}...", level="WARNING")
            return False
        return True

    def boot_up(self):
        self.log("Froeling ESP Interface Booted. Modbus watchdog active.")
        
        # Monitor Modbus health
        self.listen_state(self.on_modbus_status_change, self.modbus_sensor)
        
        # Monitor target temperature to trigger pump clearance
        self.listen_state(self.on_target_temp_change, self.target_temp_helper)
        
        # Initial check in case it's already down at boot
        if self.get_state(self.modbus_sensor) == "off":
            self.on_modbus_status_change(self.modbus_sensor, None, None, "off", None)
            
        # Run an initial check on the pump status
        self.check_and_enable_hk2()

    def on_target_temp_change(self, entity, attribute, old, new, kwargs):
        """Triggered whenever the target flow temperature is updated."""
        try:
            if float(new) > 0:
                self.check_and_enable_hk2()
        except (ValueError, TypeError):
            pass

    def check_and_enable_hk2(self):
        """Checks if HK2 is enabled and switches it on if heating is required."""
        if not self.hk2_pump_control:
            self.log("HK2 Pump Control entity not found in GlobalSettings.", level="ERROR")
            return

        current_state = self.get_state(self.hk2_pump_control)
        
        # Assuming 'on' or 'ON' is the required state for the select entity
        # Adjust 'ON' to the exact option string used by your Fröling Modbus integration
        if current_state not in ["on", "ON"]:
            self.log(f"Heating requested. Switching {self.hk2_pump_control} to ON.", level="INFO")
            self.call_service("select/select_option", 
                              entity_id=self.hk2_pump_control, 
                              option="ON")

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
