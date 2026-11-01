import pytest
from src.devices.smart_plug import SmartPlug


def test_smart_plug_initial_state(sample_plug: SmartPlug):
    """Vérifie l'état par défaut de la prise lors de son instanciation."""
    assert sample_plug.device_id == "prise_test"
    assert sample_plug.name == "Prise Machine à Laver"
    assert sample_plug.is_on is False
    assert sample_plug.power_w == 0.0


def test_smart_plug_handle_command_on(sample_plug: SmartPlug):
    """Vérifie le passage à l'état ON suite à une commande."""
    sample_plug.handle_command("ON")
    assert sample_plug.is_on is True
    assert sample_plug.power_w == 2000.0


def test_smart_plug_handle_command_off(sample_plug: SmartPlug):
    """Vérifie le passage à l'état OFF depuis un état ON."""
    sample_plug.handle_command("ON")
    sample_plug.handle_command("OFF")
    assert sample_plug.is_on is False
    assert sample_plug.power_w == 0.0


def test_smart_plug_handle_command_case_insensitive(sample_plug: SmartPlug):
    """Vérifie la robustesse face aux espaces et minuscules/majuscules."""
    sample_plug.handle_command("  on  ")
    assert sample_plug.is_on is True
    assert sample_plug.power_w == 2000.0

    sample_plug.handle_command("off\n")
    assert sample_plug.is_on is False
    assert sample_plug.power_w == 0.0


def test_smart_plug_handle_unknown_command(sample_plug: SmartPlug):
    """S'assure qu'une commande inconnue ne modifie pas l'état actuel."""
    sample_plug.handle_command("ON")
    sample_plug.handle_command("UNKNOWN_ACTION")
    assert sample_plug.is_on is True
    assert sample_plug.power_w == 2000.0


def test_smart_plug_update_loop(sample_plug: SmartPlug):
    """Vérifie l'actualisation de la puissance consommée lors du cycle de simulation."""
    # Test à l'état OFF -> consommation de veille
    sample_plug.update(delta_time_s=1.0)
    assert sample_plug.power_w == 1.2

    # Test à l'état ON -> consommation nominale
    sample_plug.handle_command("ON")
    sample_plug.update(delta_time_s=1.0)
    assert sample_plug.power_w == 2000.0