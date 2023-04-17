"""Tests for BLE devices"""
# pylint: disable=line-too-long
from lennoxs30api.s30api_async import lennox_system

from tests.conftest import loadfile


def test_ble_config(api_system_04_furn_ac_zoning):
    """Tests BLE config loading"""
    api = api_system_04_furn_ac_zoning
    system: lennox_system = api.system_list[0]
    assert system.sysId == "LCC"

    message = loadfile("s40_ble.json", "LCC")
    system.processMessage(message)

    assert len(system.ble_devices) == 3

    ble_device = system.ble_devices[768]
    assert ble_device.ble_id == 768
    assert ble_device.deviceName == "s40 1"
    assert ble_device.deviceType == "tstat"
    assert ble_device.controlModelNumber == "107088-01"
    assert ble_device.controlSerialNumber == "BT23A09840"
    assert ble_device.controlHardwareVersion == "A"
    assert ble_device.controlSoftwareVersion == "04.15.0012"
    assert ble_device.commStatus == "unKnown"
    assert len(ble_device.inputs) == 0

    ble_device = system.ble_devices[512]
    assert ble_device.ble_id == 512
    assert ble_device.deviceName == "Master Bedroom"
    assert ble_device.deviceType == "ras"
    assert ble_device.controlModelNumber == "22V25"
    assert ble_device.controlSerialNumber == "TS22M01658"
    assert ble_device.controlHardwareVersion == "B"
    assert ble_device.controlSoftwareVersion == "04.00.0481"
    assert ble_device.commStatus == "active"
    assert len(ble_device.inputs) == 17
    input_sensor = ble_device.inputs[4000]
    assert input_sensor.name == "rssi"
    assert input_sensor.value == "-58"
    assert input_sensor.unit == "none"
    input_sensor = ble_device.inputs[4061]
    assert input_sensor.name == "RAS Analog Temp status"
    assert input_sensor.value == "0"
    assert input_sensor.unit == "none"
    input_sensor = ble_device.inputs[4060]
    assert input_sensor.name == "RAS Analog Temp"
    assert input_sensor.value == "66.970001"
    assert input_sensor.unit == "Fahreheit"

    ble_device = system.ble_devices[513]
    assert ble_device.ble_id == 513
    assert ble_device.deviceName == "Basement"
    assert ble_device.deviceType == "ras"
    assert ble_device.controlModelNumber == "22V25"
    assert ble_device.controlSerialNumber == "TS22M01659"
    assert ble_device.controlHardwareVersion == "B"
    assert ble_device.controlSoftwareVersion == "04.00.0481"
    assert ble_device.commStatus == "active"
    assert len(ble_device.inputs) == 17


class CallbackHandler(object):
    """Handler for callbacks"""

    def __init__(self):
        self.called = 0

    def update_callback(self):
        """Callback for changes"""
        self.called = self.called + 1


def test_ble_device_subscriptions(api_system_04_furn_ac_zoning):
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
