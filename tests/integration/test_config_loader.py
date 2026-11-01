from pathlib import Path
import yaml
import pytest

from src.devices.smart_plug import SmartPlug


def test_load_yaml_configuration(temp_config_file: Path):
    """Vérifie la lecture et le parsing du fichier de configuration YAML."""
    with open(temp_config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    assert "mqtt" in config
    assert "devices" in config
    assert config["mqtt"]["broker"] == "127.0.0.1"
    assert len(config["devices"]) == 1


def test_instantiate_devices_from_config(sample_config: dict):
    """Vérifie l'instanciation dynamique des objets virtuels à partir de la configuration."""
    devices = []
    for dev_conf in sample_config["devices"]:
        if dev_conf["type"] == "smart_plug":
            plug = SmartPlug(
                device_id=dev_conf["id"],
                name=dev_conf["name"],
                nominal_power=dev_conf["nominal_power"],
                standby_power=dev_conf.get("standby_power", 0.0),
            )
            devices.append(plug)

    assert len(devices) == 1
    assert isinstance(devices[0], SmartPlug)
    assert devices[0].device_id == "prise_virtuelle_1"
    assert devices[0].nominal_power == 1500.0
    assert devices[0].standby_power == 0.5