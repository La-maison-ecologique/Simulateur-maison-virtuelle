# tests/conftest.py
import sys
import yaml
from pathlib import Path
from unittest.mock import MagicMock
import pytest

# Garantie que la racine du projet est dans sys.path quel que soit le lieu d'exécution
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.devices.smart_plug import SmartPlug


@pytest.fixture
def sample_config() -> dict:
    """Fournit une configuration de test valide en dictionnaire."""
    return {
        "mqtt": {
            "broker": "127.0.0.1",
            "port": 1883,
            "username": "simulateur",
            "password": "secret_password",
            "discovery_prefix": "homeassistant",
        },
        "devices": [
            {
                "id": "prise_virtuelle_1",
                "name": "Prise Test",
                "type": "smart_plug",
                "nominal_power": 1500.0,
                "standby_power": 0.5,
            }
        ],
    }


@pytest.fixture
def sample_plug() -> SmartPlug:
    """Instancie une prise virtuelle standard pour les tests."""
    return SmartPlug(
        device_id="prise_test",
        name="Prise Machine à Laver",
        nominal_power=2000.0,
        standby_power=1.2,
    )


@pytest.fixture
def temp_config_file(tmp_path: Path, sample_config: dict) -> Path:
    """Crée un fichier YAML temporaire sur le disque pour tester le chargement de config."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "config.yaml"
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.dump(sample_config, f)
    return config_file