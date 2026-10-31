from abc import ABC, abstractmethod

class BaseDevice(ABC):
    def __init__(self, device_id: str, name: str):
        self.device_id = device_id
        self.name = name

    @abstractmethod
    def update(self, delta_time_s: float):
        """Mise à jour de l'état interne et physique du composant."""
        pass

    @abstractmethod
    def handle_command(self, payload: str):
        """Réception des ordres émis par Home Assistant."""
        pass