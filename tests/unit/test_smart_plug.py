import pytest
from src.devices.smart_plug import SmartPlug

def test_smart_plug_initial_state():
    plug = SmartPlug(device_id="test_plug", name="Prise Test", nominal_power=1000.0, standby_power=1.0)
    assert plug.is_on is False
    assert plug.power_w == 0.0

def test_smart_plug_handle_command_on():
    plug = SmartPlug(device_id="test_plug", name="Prise Test", nominal_power=1000.0, standby_power=1.0)
    
    # Envoi de la commande ON
    plug.handle_command("ON")
    assert plug.is_on is True
    assert plug.power_w == 1000.0

def test_smart_plug_update_standby():
    plug = SmartPlug(device_id="test_plug", name="Prise Test", nominal_power=1000.0, standby_power=1.5)
    
    # Si la prise est OFF, update() applique la consommation de veille
    plug.update(delta_time_s=1.0)
    assert plug.power_w == 1.5