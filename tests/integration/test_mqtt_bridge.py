import json
from unittest.mock import MagicMock, patch
import pytest

from src.bridge.mqtt_bridge import MQTTBridge
from src.devices.smart_plug import SmartPlug


def test_mqtt_bridge_init(sample_config: dict, sample_plug: SmartPlug):
    """Vérifie la création du client MQTT avec l'API v2."""
    with patch("paho.mqtt.client.Client") as mock_client_cls:
        bridge = MQTTBridge(sample_config["mqtt"], [sample_plug])
        mock_client_cls.assert_called_once()
        assert bridge.devices["prise_test"] == sample_plug


def test_mqtt_bridge_discovery_payloads(sample_config: dict, sample_plug: SmartPlug):
    """Valide la structure et le contenu des messages Home Assistant Discovery."""
    bridge = MQTTBridge(sample_config["mqtt"], [sample_plug])
    bridge.client = MagicMock()

    bridge._publish_discovery()

    # Le pont doit publier 2 configurations : 1 switch et 1 sensor de puissance
    assert bridge.client.publish.call_count == 2

    call_args_list = bridge.client.publish.call_args_list
    topics = [call[0][0] for call in call_args_list]

    expected_switch_topic = "homeassistant/switch/sim_prise_test/config"
    expected_sensor_topic = "homeassistant/sensor/sim_prise_test_power/config"

    assert expected_switch_topic in topics
    assert expected_sensor_topic in topics

    # Inspection du contenu du payload switch
    for call in call_args_list:
        topic, payload_json = call[0][0], call[0][1]
        retain = call[1].get("retain", False) or (len(call[0]) > 2 and call[0][2])

        if topic == expected_switch_topic:
            payload = json.loads(payload_json)
            assert payload["name"] == "Prise Machine à Laver"
            assert payload["command_topic"] == "house/sim/switch/prise_test/set"
            assert payload["state_topic"] == "house/sim/switch/prise_test/state"
            assert payload["payload_on"] == "ON"
            assert payload["payload_off"] == "OFF"


def test_mqtt_bridge_on_connect_subscribes(sample_config: dict, sample_plug: SmartPlug):
    """Vérifie que la connexion réussie (reason_code=0) déclenche l'abonnement aux topics."""
    bridge = MQTTBridge(sample_config["mqtt"], [sample_plug])
    bridge.client = MagicMock()

    # Simulation de la réponse de connexion du broker MQTT v2
    bridge._on_connect(
        client=bridge.client,
        userdata=None,
        flags={},
        reason_code=0,
    )

    bridge.client.subscribe.assert_called_once_with("house/sim/switch/prise_test/set")


def test_mqtt_bridge_on_message_handles_command(sample_config: dict, sample_plug: SmartPlug):
    """Vérifie que la réception d'un message MQTT exécute la commande sur l'appareil."""
    bridge = MQTTBridge(sample_config["mqtt"], [sample_plug])
    bridge.client = MagicMock()

    # Création d'un message simulé provenant de Home Assistant
    mock_msg = MagicMock()
    mock_msg.topic = "house/sim/switch/prise_test/set"
    mock_msg.payload.decode.return_value = "ON"

    assert sample_plug.is_on is False

    bridge._on_message(bridge.client, None, mock_msg)

    # L'appareil doit être ON et avoir publié son nouvel état
    assert sample_plug.is_on is True
    assert sample_plug.power_w == 2000.0
    bridge.client.publish.assert_any_call(
        "house/sim/switch/prise_test/state", "ON", retain=True
    )


def test_mqtt_bridge_publish_device_state(sample_config: dict, sample_plug: SmartPlug):
    """Vérifie la publication régulière de la télémétrie de puissance."""
    bridge = MQTTBridge(sample_config["mqtt"], [sample_plug])
    bridge.client = MagicMock()

    sample_plug.handle_command("ON")
    bridge.publish_device_state(sample_plug)

    bridge.client.publish.assert_any_call(
        "house/sim/switch/prise_test/state", "ON", retain=True
    )
    bridge.client.publish.assert_any_call(
        "house/sim/sensor/prise_test_power/state", "2000.0", retain=True
    )