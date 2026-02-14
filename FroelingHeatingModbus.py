
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
