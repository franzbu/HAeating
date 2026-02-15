'''
    20260101

    AppDaemon watchdog

    combines forces with automation 'AppDaemon Watchdog'

    Regular shutdown/restart of AppDaemon: 'input_boolean.appdaemon_running' is switched off if automation (named "AppDaemon Watchdog") 
    is missing 'pulse' initiated by this module (as attribute to input_boolean.appdaemon_running). 

    Automation (aside from switching off 'input_boolean.appdaemon_running' in case of missing 'heartbeat', the automations also sends a warning):

        alias: AppDaemon Watchdog
        description: for power_outage_report.py
        triggers:
        - value_template: >
            {% set last = state_attr('input_boolean.appdaemon_running',
            'last_heartbeat') %} {% if last is not none %}
                {{ (now() - as_datetime(last)).total_seconds() > 90 }}
            {% else %}
                false
            {% endif %}
            trigger: template
        actions:
        - action: input_boolean.turn_off
            target:
            entity_id: input_boolean.appdaemon_running
        - action: telegram_bot.send_message
            metadata: {}
            data:
            target: 79867494
            title: ⚠️ AppDaemon Alert
            message: AppDaemon - heartbeat stopped.
            disable_notification: true


'''

from appdaemon.plugins.hass import Hass # type: ignore
from datetime import timedelta

class ADWD(Hass):    
    def initialize(self):
        pass
        self.run_every(self.pulse, 'now', 60)

    def pulse(self, kwargs):
        self.turn_on("input_boolean.appdaemon_running")
        iso_time = self.get_now().replace(microsecond=0).isoformat()
        self.set_state("input_boolean.appdaemon_running", state="on", attributes={"last_heartbeat": iso_time})
