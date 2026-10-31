from src.devices.base_device import BaseDevice

class SmartPlug(BaseDevice):
    def __init__(self, device_id: str, name: str, nominal_power: float, standby_power: float = 0.0):
        super().__init__(device_id, name)
        self.nominal_power = nominal_power
        self.standby_power = standby_power
        self.is_on = False
        self.power_w = 0.0

    def handle_command(self, payload: str):
        command = payload.strip().upper()
        if command == "ON":
            self.is_on = True
            self.power_w = self.nominal_power
        elif command == "OFF":
            self.is_on = False
            self.power_w = 0.0

    def update(self, delta_time_s: float):
        # En veille ou en fonctionnement
        if self.is_on:
            self.power_w = self.nominal_power
        else:
            self.power_w = self.standby_power