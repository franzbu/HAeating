
''' apps.yaml
global_config:
  heating_map:
    froeling_boiler_1_desired_temperature: 'number.froeling_central_gateway_boiler_1_target_temperature'
    froeling_boiler_1_pump_control: 'sensor.froeling_central_gateway_boiler_1_pump_control'
    froeling_boiler_1_pump_on_off: 'binary_sensor.froeling_central_gateway_boiler_1_pump_status' 
    froeling_boiler_1_top_temp: 'sensor.froeling_central_gateway_boiler_1_temperature_top'
    froeling_boiler_state: 'sensor.froeling_central_gateway_boiler_state'
    froeling_boiler_target_temperature: 'number.froeling_central_gateway_boiler_target_temperature'
    froeling_boiler_temp: 'sensor.froeling_central_gateway_boiler_temperature'
    froeling_buffer_1_charge_state: 'sensor.froeling_central_gateway_buffer_1_charge_state'
    froeling_buffer_1_pump_control: 'sensor.froeling_central_gateway_buffer_1_pump_control'
    froeling_buffer_1_pump_on_off: 'binary_sensor.froeling_central_gateway_buffer_1_pump_on_off' 
    froeling_buffer_temp_1: 'sensor.froeling_central_gateway_buffer_1_temperature_sensor_1'
    froeling_buffer_temp_2: 'sensor.froeling_central_gateway_buffer_1_temperature_sensor_2'
    froeling_buffer_temp_3: 'sensor.froeling_central_gateway_buffer_1_temperature_sensor_3'
    froeling_buffer_temp_4: 'sensor.froeling_central_gateway_buffer_1_temperature_sensor_4'
    froeling_collector_flow_temp: 'sensor.froeling_central_gateway_collector_flow_temperature'
    froeling_collector_pump_control: 'sensor.froeling_central_gateway_collector_pump_control'
    froeling_collector_return_temp: 'sensor.froeling_central_gateway_collector_return_temperature'
    froeling_collector_shutdown_delta: 'number.froeling_central_gateway_collector_shutdown_difference'
    froeling_collector_startup_delta: 'number.froeling_central_gateway_collector_startup_difference'
    froeling_collector_temp: 'sensor.froeling_central_gateway_collector_temperature'
    froeling_current_control_of_the_collector_boiler_pump: 'sensor.froeling_central_gateway_collector_boiler_pump_control'
    froeling_exhaust_temp: 'sensor.froeling_central_gateway_boiler_flue_gas_temperature'
    froeling_hk2_flow_actual_temp: 'sensor.froeling_central_gateway_hk2_flow_actual_temperature'
    froeling_hk2_flow_target_temp: 'sensor.froeling_central_gateway_hk2_flow_target_temperature'
    froeling_hk2_flow_temp_external: 'number.froeling_central_gateway_hk02_flow_setpoint_external'
    froeling_hk2_flow_temp_threshold_pump_off: 'number.froeling_central_gateway_hk02_heating_circuit_pump_off_when_flow_target_is_less_than'
    froeling_hk2_frost_protection_temperature: 'number.froeling_central_gateway_hk02_frost_protection_temperature'
    froeling_hk2_operating_mode: 'select.froeling_central_gateway_hk02_operating_mode'
    froeling_hk2_pump_external: 'select.froeling_central_gateway_hk02_clearance_external_specification'
    froeling_hk2_pump_on_off: 'binary_sensor.froeling_central_gateway_hk02_pump_status' 
    froeling_induced_draft_control: 'sensor.froeling_central_gateway_boiler_induced_draught_control'
    froeling_induced_draft_speed: 'sensor.froeling_central_gateway_boiler_induced_draught_speed'
    froeling_outside_temperature: 'sensor.froeling_central_gateway_boiler_outside_temperature'
    froeling_oxygen_controller: 'sensor.froeling_central_gateway_boiler_oxygen_controller'
    froeling_primary_air: 'sensor.froeling_central_gateway_boiler_primary_air'
    froeling_remaining_heating_hours_until_ash_emptying_warning: 'sensor.froeling_central_gateway_boiler_remaining_heating_hours_until_ash_emptying_warning'
    froeling_residual_oxygen_content: 'sensor.froeling_central_gateway_boiler_residual_oxygen_content'
    froeling_return_sensor: 'sensor.froeling_central_gateway_boiler_return_sensor'
    froeling_system_state: 'sensor.froeling_central_gateway_boiler_system_state'
    froeling_hk2_flow_targt_temp_external: 'number.froeling_central_gateway_hk2_flow_target_temp'

'''

import hassapi as hass  # type: ignore
from datetime import datetime, timedelta, time

# ==================================================================================================
# HEATING AUTOMATION (Per Room Demand Calculator)
# ==================================================================================================
class HeatingAutomation(hass.Hass):     
    def initialize(self):
        self.gl = self.get_app("global_config")
        # Extract location from app name to allow code reuse across multiple rooms
        self.location = self.name.removeprefix("heating_") 
        self.sensor_temp = self.gl.get_room_temp(self.location)
        self.mode_mapping = {'Standard': 'standard', 'Holiday': 'holiday', 'Temporary': 'temp', 'Party': 'party'}
        self.delay_timer = None

        # Dynamically build schedule list to ensure the app reacts to all potential mode changes
        self.my_schedules = [f'schedule.{s}_{self.location}' for s in list(self.mode_mapping.values()) + ['off']]
        
        for sched in self.my_schedules:
            if self.entity_exists(sched):
                self.listen_state(self.callback_debounced_refresh, sched)
                self.listen_state(self.callback_debounced_refresh, sched, attribute='temp')
                self.listen_state(self.callback_debounced_refresh, sched, attribute='next_event')

        self.listen_event(self.on_config_change, "entity_registry_updated")
        self.listen_state(self.callback_debounced_refresh, f'input_select.heating_schedule_{self.location}')
        self.listen_state(self.callback_temp_sensor, f'input_number.target_temp_{self.location}')
        self.listen_state(self.callback_debounced_refresh, f'input_number.delta_temp_{self.location}')
        self.listen_state(self.callback_temp_sensor, self.sensor_temp)
        
        # --- SOLAR CONFIGURATION ---
        # If missing from apps.yaml, defaults to None (Feature Disabled)
        self.solar_activation_temp = self.args.get("solar_activation_temp")
        self.solar_peak_temp = self.args.get("solar_peak_temp")

        # SUN COMPENSATION: Listen to Garten Temp and the room-specific helper
        self.garten_temp_sensor = self.gl.get_outdoor_temp("garten_temp")
        self.sun_comp_helper = f"input_number.sun_compensation_{self.location}"
        
        self.listen_state(self.callback_temp_sensor, self.garten_temp_sensor)
        if self.entity_exists(self.sun_comp_helper):
            self.listen_state(self.callback_temp_sensor, self.sun_comp_helper)
        
        # Listen to the Input Select for Master Off, auto, heating, party
        self.listen_state(self.callback_master_switch, "input_select.heating_mode")

        self.boost_helper = f"input_boolean.boost_enabled_{self.location}"
        if self.entity_exists(self.boost_helper):
            self.listen_state(self.callback_temp_sensor, self.boost_helper)
            self.listen_state(self.callback_temp_sensor, "input_number.heating_boost_threshold")
            self.listen_state(self.callback_temp_sensor, "input_number.heating_boost_factor")

        self.listen_event(self.force_refresh_handler, "HEATING_FORCE_EVALUATION")

        self.run_in(self.first_evaluation, 5)

    def force_refresh_handler(self, event_name, data, kwargs):
        entity = f'input_boolean.heating_claim_{self.location}'
        self.turn_off(entity)
        self.refresh_logic(force_reset=True)

    def on_config_change(self, event_name, data, kwargs):
        if data.get("entity_id", "") in self.my_schedules:
            self.prepare_dashboard_next_event()

    def callback_debounced_refresh(self, entity, attribute, old, new, args):
        self.update_dashboard_msg('Calculating next event...')
        if self.delay_timer:
            try: self.cancel_timer(self.delay_timer)
            except: pass
        self.delay_timer = self.run_in(self.first_evaluation, 1)

    def first_evaluation(self, kwargs):
        self.delay_timer = None
        self.refresh_logic(force_reset=False)
        self.prepare_dashboard_next_event()

    def callback_master_switch(self, entity, attribute, old, new, args):
        self.evaluate_heating_claim()

    def callback_temp_sensor(self, entity, attribute, old, new, args):
        self.evaluate_heating_claim() 

    def refresh_logic(self, force_reset=False):
        curr_sched = self.current_schedule()
        
        if curr_sched == f'schedule.off_{self.location}':
            target = 5.0
            self.set_target_temp(target)
            self.update_heating_claim(False)
            self.update_boost_attributes(0.0, 0.0, "off")
            self.update_sun_sensor(0.0)
            return 

        if self.current_schedule_active():
            sched_temp = self.get_state(curr_sched, attribute='temp')
            try: 
                target = float(sched_temp)
            except: 
                target = self.heat_temp() 
        else:
            target = self.base_temp()

        self.set_target_temp(target)
        
        # Calculate offset and update sensor once
        sun_offset = self.get_sun_offset()
        self.update_sun_sensor(sun_offset)
        
        effective_target = target - sun_offset
        self.evaluate_heating_claim(override_target=effective_target, force_reset=force_reset)

    def evaluate_heating_claim(self, override_target=None, force_reset=False):
        if self.get_state("input_select.heating_mode") == "Off":
            self.update_heating_claim(False)
            self.update_boost_attributes(0.0, 0.0, "off")
            return

        if self.current_schedule() == f'schedule.off_{self.location}' or not self.current_schedule_active():
            self.update_heating_claim(False)
            self.update_boost_attributes(0.0, 0.0, "off")
            return
            
        curr_t = self.current_temp()
        targ_t = override_target if override_target is not None else self.target_temp()
        if curr_t is None: return

        current_state = self.get_state(f'input_boolean.heating_claim_{self.location}')
        has_claim = (current_state == 'on') if not force_reset else False
        
        upper_bound = targ_t - self.margin()
        lower_bound = targ_t - self.delta()

        if curr_t >= upper_bound:
            has_claim = False
        elif curr_t < lower_bound:
            has_claim = True

        self.update_heating_claim(has_claim)
        self.calculate_and_update_boost(curr_t, targ_t)

    def calculate_and_update_boost(self, curr_t, targ_t):
        boost_enabled = "off"
        if self.entity_exists(f"input_boolean.boost_enabled_{self.location}"):
            boost_enabled = self.get_state(f"input_boolean.boost_enabled_{self.location}")
        
        factor = float(self.get_state("input_number.heating_boost_factor") or 1.0)
        threshold = float(self.get_state("input_number.heating_boost_threshold") or 4.0)
        
        raw_boost = 0.0
        if boost_enabled == "on" and (targ_t - curr_t) >= threshold:
            raw_boost = round(max(0.0, (targ_t - curr_t) * factor), 1)
        
        self.update_boost_attributes(raw_boost, raw_boost, boost_enabled)

    def update_boost_attributes(self, contribution, raw_boost, boost_enabled):
        ent_status = f"binary_sensor.boost_status_{self.location}"
        if boost_enabled is None or boost_enabled not in ["on", "off"]:
            boost_enabled = "off"
        
        try:
            is_active = float(contribution) > 0
        except:
            is_active = False

        status_state = "on" if is_active else "off"
        icon = "mdi:fire-alert" if is_active else "mdi:fire"
        if boost_enabled == "off":
            icon = "mdi:fire-off"
        
        self.set_state(ent_status, state=status_state, attributes={
            "friendly_name": f"Boost Status {self.location.capitalize()}",
            "boost": contribution if contribution is not None else 0.0,
            "raw_boost": raw_boost if raw_boost is not None else 0.0,
            "boost_enabled": str(boost_enabled),
            "icon": icon
        })

    def current_temp(self):
        try: 
            val = self.get_state(self.sensor_temp)
            return float(val) if val not in [None, "unavailable", "unknown"] else None
        except: return None

    # ==============================================================================================
    # SOLAR COMPENSATION LOGIC
    # ==============================================================================================
    def get_sun_offset(self):
        """Pure Query: Calculates offset based on greenhouse heat."""
        if self.solar_activation_temp is None or self.solar_peak_temp is None:
            return 0.0

        if not self.entity_exists(self.sun_comp_helper):
            return 0.0
            
        try:
            max_comp = float(self.get_state(self.sun_comp_helper) or 0)
            if max_comp == 0:
                return 0.0

            raw_g = self.get_state(self.garten_temp_sensor)
            if raw_g in [None, "unavailable", "unknown"]:
                return 0.0
            g_temp = float(raw_g)
            
            start_t = float(self.solar_activation_temp)
            peak_t = float(self.solar_peak_temp)

            if g_temp <= start_t:
                factor = 0.0
            elif g_temp >= peak_t:
                factor = 1.0
            else:
                denom = peak_t - start_t
                factor = (g_temp - start_t) / denom if denom != 0 else 0.0

            return round(factor * max_comp, 2)

        except Exception as e:
            self.log(f"Solar Calc Error: {e}", level="WARNING")
            return 0.0

    def update_sun_sensor(self, offset):
        """Command: Updates the HA binary sensor."""
        ent_sun = f"binary_sensor.sun_compensation_{self.location}"
        is_active = offset > 0
        g_val = self.get_state(self.garten_temp_sensor)
        
        self.set_state(ent_sun, state="on" if is_active else "off", attributes={
            "friendly_name": f"Sun Compensation {self.location.capitalize()}",
            "compensation": offset,
            "garten_temp": g_val,
            "icon": "mdi:weather-sunny-alert" if is_active else "mdi:weather-sunny"
        })

    def target_temp(self):
        """Pure Query: Returns current target minus calculated sun offset."""
        try: 
            val = float(self.get_state(f'input_number.target_temp_{self.location}'))
            return val - self.get_sun_offset()
        except: return 5.0

    def base_temp(self):
        try: return float(self.get_state(f'input_number.base_temp_{self.location}'))
        except: return 5.0

    def delta(self):
        try: return float(self.get_state(f'input_number.delta_temp_{self.location}'))
        except: return 2

    def margin(self):
        try: return float(self.get_state('input_number.heating_margin'))
        except: return 0.5

    def heat_temp(self):
        try: return float(self.get_state(f'input_number.heat_temp_{self.location}'))
        except: return 21.0

    def current_schedule(self):
        mode = self.get_state(f'input_select.heating_schedule_{self.location}')
        suffix = self.mode_mapping.get(mode, 'off')
        return f'schedule.{suffix}_{self.location}'
    
    def current_schedule_active(self):
        return self.get_state(self.current_schedule()) == 'on'

    def set_target_temp(self, x):
        try:
            if float(self.get_state(f'input_number.target_temp_{self.location}')) == x: return
        except: pass
        self.call_service("input_number/set_value", entity_id=f'input_number.target_temp_{self.location}', value=x)

    def update_heating_claim(self, has_claim):
        entity = f'input_boolean.heating_claim_{self.location}'
        new_state = 'on' if has_claim else 'off'
        if self.get_state(entity) != new_state:
            self.turn_on(entity) if has_claim else self.turn_off(entity)

    def update_dashboard_msg(self, msg):
        self.call_service("input_text/set_value", entity_id=f'input_text.next_event_{self.location}', value=msg)

    def prepare_dashboard_next_event(self):
        curr_sched = self.current_schedule()
        self.last_schedule_response = self.call_service("schedule/get_schedule", entity_id=curr_sched)
        self.run_in(self.calculate_relay_chain, 1, sched_entity=curr_sched)

    def calculate_relay_chain(self, kwargs):
        if self.delay_timer is not None:
            return
        curr_sched = kwargs["sched_entity"]
        try:
            full_data = self.last_schedule_response
            res_obj = full_data.get("result", {}).get("response", {})
            rules_dict = res_obj.get(curr_sched, {})
            next_event_str = self.get_state(curr_sched, attribute='next_event')
            if not rules_dict or not next_event_str or next_event_str == "None":
                self.update_dashboard_msg('No heating scheduled.')
                return
            event_dt = datetime.strptime(next_event_str, '%Y-%m-%dT%H:%M:%S%z').astimezone()
            if self.current_schedule_active():
                true_end_dt = self.find_true_chain_end(event_dt, rules_dict)
                limit_dt = event_dt + timedelta(days=7)
                msg = 'Heating stops at next power cut ;)' if true_end_dt >= limit_dt else f"Heating stops at {self.format_time_msg(true_end_dt)}"
            else:
                msg = f"Heating starts at {self.format_time_msg(event_dt)}"
            self.update_dashboard_msg(msg)
        except Exception as e:
            self.log(f"Response Evaluation Error: {e}")

    def find_true_chain_end(self, start_dt, rules_dict):
        current_dt = start_dt
        limit_dt = start_dt + timedelta(days=7)
        while current_dt < limit_dt:
            day_name = current_dt.strftime('%A').lower()
            day_rules = rules_dict.get(day_name, [])
            found_link = False
            for block in day_rules:
                try:
                    f_str = block.get('from')
                    f_time = datetime.strptime(f_str, '%H:%M:%S' if len(f_str) > 5 else '%H:%M').time()
                    block_start_dt = datetime.combine(current_dt.date(), f_time).replace(tzinfo=current_dt.tzinfo)
                    if abs((block_start_dt - current_dt).total_seconds()) <= 65:
                        to_str = block.get('to')
                        if ".999999" in to_str:
                            current_dt = (current_dt + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                        else:
                            t_parts = [int(p) for p in to_str.split(':')]
                            current_dt = current_dt.replace(hour=t_parts[0], minute=t_parts[1], second=t_parts[2] if len(t_parts) > 2 else 0, microsecond=0)
                        found_link = True
                        break 
                except: continue
            if not found_link: break
        return current_dt

    def format_time_msg(self, date_obj):
        now = datetime.now(date_obj.tzinfo)
        if date_obj.date() == now.date(): return date_obj.strftime('%H:%M.')
        elif date_obj.date() == (now + timedelta(days=1)).date(): return date_obj.strftime('%H:%M tomorrow.')
        else: return date_obj.strftime('%H:%M on %d.%m.')

        
# ==================================================================================================
# HEATING PUMP CONTROL (Central Boiler Logic)
# ==================================================================================================
class HeatingPumpControl(hass.Hass):
    def initialize(self):
        # PHASE 1: Static Initialization (Runs ONCE)
        self.gl = self.get_app("global_config")
        raw_deps = self.args.get('dependencies', [])
        self.managed_locations = [d.replace("heating_", "") for d in raw_deps if d not in ["global_config", "heating_pump_control"]]
        
        self.valve_map = self.gl.args.get("valve_map", {})
        self.flow_target_helper = "input_number.hk2_target_flow_temp"     
        self.mode_select = "input_select.heating_mode"
        self.modbus_status_sensor = "binary_sensor.froeling_central_gateway_esp_modbus_status"

        self.ext_temp_sensor = self.gl.get_outdoor_temp()
        self.telegram_target = self.args.get('telegram_id') 
        
        self.debounce_timer = None
        self.claim_start_times = {} 
        self.startup_timer = None

        # Start the health check loop
        self.try_startup()

    def try_startup(self, kwargs=None):
        # PHASE 2: Health Check Loop
        if not self.check_system_health():
            self.startup_timer = self.run_in(self.try_startup, 30)
            return

        # PHASE 3: Boot (Only reached when healthy)
        self.boot_up()

    def check_system_health(self):
        critical_entities = [
            self.flow_target_helper,
            self.ext_temp_sensor,
            self.mode_select,
            self.modbus_status_sensor
        ]
        
        missing = []
        unavailable = []
        
        for entity in critical_entities:
            if not self.entity_exists(entity):
                missing.append(entity)
                continue
            
            state = self.get_state(entity)
            if state in ["unavailable", "unknown", None]:
                unavailable.append(f"{entity} ({state})")

        if missing:
            self.log(f"CRITICAL: Entities missing: {missing}", level="ERROR")
            return False

        if unavailable:
            self.log(f"Startup delayed. Waiting for: {unavailable}", level="WARNING")
            return False
        
        return True

    def boot_up(self):
        self.log("System Healthy. Registering listeners.")
        
        for loc in self.managed_locations:
            self.listen_state(self.callback_debounced_eval, f"input_boolean.heating_claim_{loc}")
            status_sensor = f"binary_sensor.boost_status_{loc}"
            self.listen_state(self.callback_debounced_eval, status_sensor, attribute="all")
            
        self.listen_state(self.callback_debounced_eval, self.ext_temp_sensor)
        self.listen_state(self.on_mode_change, self.mode_select)
        self.listen_state(self.on_modbus_failure, self.modbus_status_sensor)
        
        config_entities = [
            "input_number.heating_baseline_0_deg",
            "input_number.baseline_adjustment",
            "input_number.max_flow_temp",
            "input_number.heating_boost_factor",
            "input_number.heating_boost_threshold",
            "input_number.heating_claim_duration",
            "input_number.flow_temp_multi_room_offset" 
        ]
        for e in config_entities:
            self.listen_state(self.callback_debounced_eval, e)
                
        self.evaluate_heating_pump()

    def on_modbus_failure(self, entity, attribute, old, new, args):
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
    
    def on_mode_change(self, entity, attribute, old, new, args):
        if new == "Off":
            self.call_service("input_number/set_value", entity_id=self.flow_target_helper, value=0)
            return
        if old == "Heating" and new == "Auto":
            self.reset_all_claims()
        self.evaluate_heating_pump()

    def reset_all_claims(self):
        for loc in self.managed_locations:
            claim = f"input_boolean.heating_claim_{loc}"
            if self.get_state(claim) == "on":
                self.turn_off(claim)

    def callback_debounced_eval(self, entity, attribute, old, new, args):
        if self.debounce_timer:
            try: self.cancel_timer(self.debounce_timer)
            except: pass 
        self.debounce_timer = self.run_in(self.retry_evaluation, 3)

    def retry_evaluation(self, kwargs):
        self.debounce_timer = None
        self.evaluate_heating_pump()

    def evaluate_heating_pump(self):
        mode = self.get_state(self.mode_select)

        if mode == "Off": 
            self.call_service("input_number/set_value", entity_id=self.flow_target_helper, value=0)
            return

        now = datetime.now()
        user_duration = int(float(self.get_state("input_number.heating_claim_duration") or 10))
        
        for loc in self.managed_locations:
            if self.get_state(f"input_boolean.heating_claim_{loc}") == 'on':
                if loc not in self.claim_start_times: self.claim_start_times[loc] = now 
            else:
                self.claim_start_times.pop(loc, None)

        active_claims = [loc for loc, start in self.claim_start_times.items() 
                         if (now - start).total_seconds() >= user_duration]

        should_heat = False
        
        if mode == "Party":
            max_valve = 0.0
            found_valves = False
            for loc in self.managed_locations:
                valve_entity = self.valve_map.get(f"valve_{loc}")
                if valve_entity and self.entity_exists(valve_entity):
                    found_valves = True
                    try:
                        val = float(self.get_state(valve_entity) or 0)
                        if val > max_valve: max_valve = val
                    except: pass
            if found_valves and max_valve < 20.0:
                self.call_service("input_select/select_option", entity_id=self.mode_select, option="Auto")
                if self.telegram_target:
                    self.notify(self.telegram_target, "🛑 Party Mode Ended", f"Valves are closed ({max_valve}%).", True)
                return 
            should_heat = True

        elif active_claims:
            should_heat = True
        else:
            should_heat = False
            self.call_service("input_number/set_value", entity_id=self.flow_target_helper, value=0)
            if mode == "Heating":
                self.call_service("input_select/select_option", entity_id=self.mode_select, option="Auto")

        if should_heat:
            raw_out = self.get_state(self.ext_temp_sensor)
            out_t = float(raw_out) if raw_out not in [None, "unavailable", "unknown"] else 0.0
            adj_factor = float(self.get_state("input_number.baseline_adjustment") or 0.4)
            baseline = (-adj_factor * out_t) + float(self.get_state("input_number.heating_baseline_0_deg") or 36.0)
            
            max_realized_boost = 0.0
            for loc in active_claims:
                realized = float(self.get_state(f"binary_sensor.boost_status_{loc}", attribute="boost") or 0.0)
                if realized > max_realized_boost:
                    max_realized_boost = realized

            multi_room_factor = float(self.get_state("input_number.flow_temp_multi_room_offset") or 0.0)
            multi_room_boost = max(0, len(active_claims) - 1) * multi_room_factor

            calc_target = float(round(baseline + max_realized_boost + multi_room_boost))
            max_f = float(self.get_state("input_number.max_flow_temp") or 45.0)
            if calc_target > max_f: calc_target = max_f
                
            self.call_service("input_number/set_value", entity_id=self.flow_target_helper, value=calc_target)
            if mode != "Heating" and mode != "Party":
                self.call_service("input_select/select_option", entity_id=self.mode_select, option="Heating")

    def notify(self, target, title, message, disable_notification=True):
        self.gl.send_telegram(target, title, message, disable_notification)
