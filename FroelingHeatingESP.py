
# ==================================================================================================
# FROELING HEATING ESP INTERFACE
# ==================================================================================================
class FroelingHeatingESP(hass.Hass):
    def initialize(self):
        self.gl = self.get_app("global_config")
        self.telegram_target = self.args.get('telegram_id')
        self.target_temp_helper = "input_number.target_flow_temp"
        self.boiler_target_helper = "input_number.hk2_target_flow_temp"
        self.modbus_sensor = "binary_sensor.froeling_modbus_status"
        
        self.startup_timer = None
        self.try_startup()

    def try_startup(self, kwargs=None):
        if not self.check_system_health():
            self.startup_timer = self.run_in(self.try_startup, 30)
            return
        self.boot_up()

    def check_system_health(self):
        # We only block on the presence of the Helpers now.
        # We don't block on the Modbus Status being 'on' anymore.
        critical_entities = [self.target_temp_helper, self.boiler_target_helper]
        
        for entity in critical_entities:
            if not self.entity_exists(entity) or self.get_state(entity) in ["unavailable", "unknown", None]:
                self.log(f"Waiting for {entity}...", level="WARNING")
                return False
        return True

    def boot_up(self):
        self.log("Froeling ESP Interface Booted.")
        
        # Listen for internal target changes
        self.listen_state(self.on_target_flow_temp_change, self.target_temp_helper)
        
        # Monitor Modbus health (now always active regardless of initial state)
        self.listen_state(self.on_modbus_status_change, self.modbus_sensor)
        
        # Initial check in case it's already down at boot
        if self.get_state(self.modbus_sensor) == "off":
            self.on_modbus_status_change(self.modbus_sensor, None, None, "off", None)

    def on_target_flow_temp_change(self, entity, attribute, old, new, args):
        if new in [None, "unavailable", "unknown"]:
            return
            
        # Optional: Only forward if Modbus is actually healthy
        if self.get_state(self.modbus_sensor) == "on":
            self.call_service("input_number/set_value", 
                              entity_id=self.boiler_target_helper, 
                              value=new)
        else:
            self.log(f"Suppressed target update to {new}°C - Modbus is Down", level="WARNING")

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
