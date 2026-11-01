import json
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

class MQTTBridge:
    def __init__(self, config: dict, devices: list):
        self.config = config
        self.devices = {dev.device_id: dev for dev in devices}
        self.client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2, client_id="VirtualHouseSimulator")
        
        if config.get("username"):
            self.client.username_pw_set(config["username"], config["password"])
            
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def start(self):
        self.client.connect(self.config["broker"], self.config["port"], keepalive=60)
        self.client.loop_start()

    def _on_connect(self, client, userdata, flags, reason_code):
        if reason_code == 0:
            self._publish_discovery()
            # Souscription aux commandes de tous les équipements
            for dev_id in self.devices:
                cmd_topic = f"house/sim/switch/{dev_id}/set"
                self.client.subscribe(cmd_topic)

    def _publish_discovery(self):
        prefix = self.config.get("discovery_prefix", "homeassistant")
        for dev_id, dev in self.devices.items():
            # Configuration du Switch dans Home Assistant
            switch_config_topic = f"{prefix}/switch/sim_{dev_id}/config"
            switch_payload = {
                "name": dev.name,
                "unique_id": f"sim_{dev_id}_switch",
                "command_topic": f"house/sim/switch/{dev_id}/set",
                "state_topic": f"house/sim/switch/{dev_id}/state",
                "payload_on": "ON",
                "payload_off": "OFF",
                "device": {
                    "identifiers": [f"sim_device_{dev_id}"],
                    "name": f"Simulateur - {dev.name}",
                    "model": "Prise Virtuelle V1",
                    "manufacturer": "Simulateur Maison"
                }
            }
            self.client.publish(switch_config_topic, json.dumps(switch_payload), retain=True)

            # Configuration du Capteur de Puissance (Sensor)
            sensor_config_topic = f"{prefix}/sensor/sim_{dev_id}_power/config"
            sensor_payload = {
                "name": f"{dev.name} Puissance",
                "unique_id": f"sim_{dev_id}_power",
                "state_topic": f"house/sim/sensor/{dev_id}_power/state",
                "unit_of_measurement": "W",
                "device_class": "power",
                "state_class": "measurement",
                "device": {
                    "identifiers": [f"sim_device_{dev_id}"]
                }
            }
            self.client.publish(sensor_config_topic, json.dumps(sensor_payload), retain=True)

    def _on_message(self, client, userdata, msg):
        topic_parts = msg.topic.split("/")
        dev_id = topic_parts[3]
        payload = msg.payload.decode("utf-8")
        
        if dev_id in self.devices:
            # Transmet la commande immédiatement à l'appareil
            device = self.devices[dev_id]
            device.handle_command(payload)
            # Publication immédiate de l'état actualisé
            self.publish_device_state(device)

    def publish_device_state(self, device):
        dev_id = device.device_id
        state_str = "ON" if device.is_on else "OFF"
        
        self.client.publish(f"house/sim/switch/{dev_id}/state", state_str, retain=True)
        self.client.publish(f"house/sim/sensor/{dev_id}_power/state", f"{device.power_w:.1f}", retain=True)