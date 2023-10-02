"""Tests for BLE devices"""
# pylint: disable=line-too-long
from lennoxs30api.s30api_async import lennox_system

from tests.conftest import loadfile


def test_iaq_config(api_system_04_furn_ac_zoning):
    """Tests BLE config loading"""
    api = api_system_04_furn_ac_zoning
    system: lennox_system = api.system_list[0]
    assert system.sysId == "LCC"
    assert system.iaq_mitigation_action == "Filtration"
    assert system.iaq_mitigation_state == "State_Paused"
    assert system.iaq_overall_index == "Fair"

    assert system.iaq_pm25_sta == 0
    assert system.iaq_pm25_sta_valid is True
    assert system.iaq_pm25_lta == 0.186265
    assert system.iaq_pm25_lta_valid is True
    assert system.iaq_pm25_component_score == "Good"

    assert system.iaq_voc_sta == 1299.726944
    assert system.iaq_voc_sta_valid is True
    assert system.iaq_voc_lta == 297.103471
    assert system.iaq_voc_lta_valid is True
    assert system.iaq_voc_component_score == "Fair"

    assert system.iaq_co2_sta == 671.416944
    assert system.iaq_co2_sta_valid is True
    assert system.iaq_co2_lta == 656.788879
    assert system.iaq_co2_lta_valid is True
    assert system.iaq_co2_component_score == "Good"


class CallbackHandler(object):
    """Handler for callbacks"""

    def __init__(self):
        self.called = 0

    def update_callback(self):
        """Callback for changes"""
        self.called = self.called + 1


def test_iaq_subscriptions(api_system_04_furn_ac_zoning):
    """Tests subscriptions"""
    api = api_system_04_furn_ac_zoning
    system: lennox_system = api.system_list[0]
    assert system.sysId == "LCC"

    message = loadfile("s40_ble.json", "LCC")
    system.processMessage(message)

    assert len(system.ble_devices) == 3
    ble_device = system.ble_devices[513]
    message = loadfile("s40_ble_status_update.json", "LCC")
    message["Data"]["ble"]["devices"][0]["device"]["devStatus"]["commStatus"] = "not_active"
    callback_handler = CallbackHandler()
    ble_device.register_on_update_callback(callback_handler.update_callback, ["commStatus"])

    # Test 1 - processing message should invoke callback
    system.processMessage(message)
    assert callback_handler.called == 1

    # Test 2 - reprocessing message should not invoke callback
    callback_handler.called = 0
    system.processMessage(message)
    assert callback_handler.called == 0


def test_ble_sensor_subscriptions(api_system_04_furn_ac_zoning):
    """Tests subscriptions"""
    api = api_system_04_furn_ac_zoning
    system: lennox_system = api.system_list[0]
    assert system.sysId == "LCC"

    message = loadfile("s40_ble.json", "LCC")
    system.processMessage(message)

    assert len(system.ble_devices) == 3
    ble_device = system.ble_devices[513]
    message = loadfile("s40_ble_status_update.json", "LCC")
    message["Data"]["ble"]["devices"][0]["device"]["devStatus"]["inputsStatus"][0]["status"]["values"][0][
        "value"
    ] = "58"

    callback_handler = CallbackHandler()
    input_sensor = ble_device.inputs[4052]
    input_sensor.register_on_update_callback(callback_handler.update_callback, ["value"])

    # Test 1 - processing message should invoke callback
    assert input_sensor.value == "54"
    system.processMessage(message)
    assert callback_handler.called == 1
    assert input_sensor.value == "58"

    # Test 2 - reprocessing message should not invoke callback
    callback_handler.called = 0
    system.processMessage(message)
    assert callback_handler.called == 0
