"""Modules to test the alerts"""

import pytest

from lennoxs30api import s30api_async
from lennoxs30api.lennox_errors import lennox_error_get_message_from_code
from lennoxs30api.s30api_async import lennox_system
from tests.conftest import loadfile


class DirtySubscription:
    """Class to test callbacks"""

    def __init__(self, system: lennox_system, attr_name: str):
        self.triggered: int = 0
        self.id = attr_name
        system.registerOnUpdateCallback(self.update_callback, [attr_name])

    def update_callback(self):
        """Updates the callback"""
        self.triggered = self.triggered + 1


def test_alerts(api_system_04_furn_ac_zoning: s30api_async):
    """Test alerts"""
    api = api_system_04_furn_ac_zoning
    system: lennox_system = api.system_list[0]
    assert system.sysId == "LCC"

    assert system.alerts_num_cleared == 46
    assert system.alerts_num_active == 2
    assert system.alerts_last_cleared_id == 45
    assert system.alerts_num_in_active_array == 2

    assert system.heatpump_low_ambient_lockout is False
    assert system.aux_heat_high_ambient_lockout is True

    alert = system.active_alerts[1]
    assert alert["code"] == 19
    assert alert["userMessageID"] == 0
    assert alert["userMessage"] == ""
    assert alert["isStillActive"] is True
    assert alert["timestampLast"] == "1636473073"
    assert alert["priority"] == "info"
    assert alert["equipmentType"] == 0
    assert alert["message"] == "High Ambient Auxiliary Heat Lockout"
    assert alert["code"] == 19
    assert alert["userMessageID"] == 0
    assert alert["userMessage"] == ""
    assert alert["isStillActive"] is True
    assert alert["timestampLast"] == "1636473073"
    assert alert["priority"] == "info"
    assert alert["equipmentType"] == 0
    assert alert["message"] == "High Ambient Auxiliary Heat Lockout"

    alert = system.active_alerts[0]
    assert alert["code"] == 434
    assert alert["userMessageID"] == 49153
    assert alert["userMessage"] == "Problem"
    assert alert["isStillActive"] is True
    assert alert["timestampLast"] == "1665497389"
    assert alert["priority"] == "moderate"
    assert alert["equipmentType"] == 18
    assert alert["message"] == "OU Inverter Communication Error To Main Control"


def test_alerts_unknown_alert(api_system_04_furn_ac_zoning):
    """Verifies that an unknown alert is properly processed"""
    api = api_system_04_furn_ac_zoning
    system: lennox_system = api.system_list[0]
    assert system.sysId == "LCC"

    sub = DirtySubscription(system, "active_alerts")

    message = loadfile("system_04_furn_ac_zoning_alerts.json", "LCC")
    message["Data"]["alerts"]["active"][0]["alert"]["code"] = 998
    system.processMessage(message)

    assert sub.triggered == 1
    assert system.alerts_num_cleared == 46
    assert system.alerts_num_active == 2
    assert system.alerts_last_cleared_id == 45
    assert system.alerts_num_in_active_array == 2

    alert = system.active_alerts[0]
    assert alert["code"] == 998
    assert alert["userMessageID"] == 49153
    assert alert["userMessage"] == "Problem"
    assert alert["isStillActive"] is True
    assert alert["timestampLast"] == "1665497389"
    assert alert["priority"] == "moderate"
    assert alert["equipmentType"] == 18
    assert alert["message"] == "unknown alert code"


@pytest.mark.parametrize(
    ("code", "message"),
    [
        (71504, "OU: Suction Temperature Sensor: Incorrect Reading"),
        (71505, "OU: Liquid Temperature Sensor: Incorrect Reading"),
        (71506, "OU: Suction Pressure Sensor: Incorrect Reading"),
        (71507, "OU: Liquid Pressure Sensor: Incorrect Reading"),
        (71508, "OU: Outdoor Temperature Sensor: Incorrect Reading"),
        (71509, "HP: Outdoor Coil Temperature Sensor: Incorrect Reading"),
        (71510, "OU: ID TXV Failure"),
        (71511, "IU: Duct or Filter Blockage"),
        (71512, "OU: High-Pressure Switch Fault"),
        (71513, "OU: Low-Pressure Switch Fault"),
        (71514, "OU: System Low on Refrigerant Charge"),
        (71515, "HP: Reversing Valve Stuck"),
        (71516, "OU: Outdoor Fan Motor Failure"),
        (71517, "IU: Indoor Fan Motor Failure"),
        (71518, "OU: Compressor Failed to Start"),
        (71519, "HP: Incorrect Reversing Valve Mode"),
        (71520, "OU: Blocked Liquid Line"),
        (71521, "HP: Outdoor TXV Failure"),
    ],
)
def test_s40_alert_codes(code, message):
    """Verify S40 alert codes use the messages from the Lennox guide."""
    assert lennox_error_get_message_from_code(code) == message


def test_alerts_no_active_alerts(api_system_04_furn_ac_zoning):
    """Verifies when no alerts are active"""
    api = api_system_04_furn_ac_zoning
    system: lennox_system = api.system_list[0]
    assert system.sysId == "LCC"

    message = loadfile("system_04_furn_ac_zoning_alerts.json", "LCC")
    message["Data"]["alerts"].pop("active")
    message["Data"]["alerts"]["meta"]["numAlertsInActiveArray"] = 0

    system.processMessage(message)

    assert system.alerts_num_cleared == 46
    assert system.alerts_num_active == 2
    assert system.alerts_last_cleared_id == 45
    assert system.alerts_num_in_active_array == 0

    assert len(system.active_alerts) == 0


# An alert code of zero indicates no alert.
def test_alerts_alert_code_0(api_system_04_furn_ac_zoning):
    """Test alert code 0"""
    api = api_system_04_furn_ac_zoning
    system: lennox_system = api.system_list[0]
    assert system.sysId == "LCC"

    message = loadfile("system_04_furn_ac_zoning_alerts.json", "LCC")
    message["Data"]["alerts"]["active"][0]["alert"]["code"] = 0
    message["Data"]["alerts"]["active"][1]["alert"]["code"] = 0
    message["Data"]["alerts"]["active"][2]["alert"]["code"] = 0
    system.processMessage(message)

    assert len(system.active_alerts) == 0


def test_alerts_lockouts(api_system_04_furn_ac_zoning):
    """Verify the alerts regarding lockout are processed into properties"""
    api = api_system_04_furn_ac_zoning
    system: lennox_system = api.system_list[0]
    assert system.sysId == "LCC"

    message = loadfile("alert_lockouts.json", "LCC")
    system.processMessage(message)

    assert system.heatpump_low_ambient_lockout is False
    assert system.aux_heat_high_ambient_lockout is True
    assert len(system.active_alerts) == 1

    alert = system.active_alerts[0]
    assert alert["code"] == 19
    assert alert["userMessageID"] == 0
    assert alert["userMessage"] == ""
    assert alert["isStillActive"] is True
    assert alert["timestampLast"] == "1636473073"
    assert alert["priority"] == "info"
    assert alert["equipmentType"] == 0
    assert alert["message"] == "High Ambient Auxiliary Heat Lockout"

    message["Data"]["alerts"]["active"][1]["alert"]["isStillActive"] = True
    system.processMessage(message)

    assert system.heatpump_low_ambient_lockout is True
    assert system.aux_heat_high_ambient_lockout is True
    assert len(system.active_alerts) == 2

    alert = system.active_alerts[0]
    assert alert["code"] == 19
    assert alert["userMessageID"] == 0
    assert alert["userMessage"] == ""
    assert alert["isStillActive"] is True
    assert alert["timestampLast"] == "1636473073"
    assert alert["priority"] == "info"
    assert alert["equipmentType"] == 0
    assert alert["message"] == "High Ambient Auxiliary Heat Lockout"

    alert = system.active_alerts[1]
    assert alert["code"] == 18
    assert alert["userMessageID"] == 0
    assert alert["userMessage"] == "Low Ambient HP Heat Lockout"
    assert alert["isStillActive"] is True
    assert alert["timestampLast"] == "1636460248"
    assert alert["priority"] == "info"
    assert alert["equipmentType"] == 0
    assert alert["message"] == "Low Ambient HP Heat Lockout"

    message["Data"]["alerts"]["active"][0]["alert"]["isStillActive"] = False
    system.processMessage(message)
    assert system.heatpump_low_ambient_lockout is True
    assert system.aux_heat_high_ambient_lockout is False
    assert len(system.active_alerts) == 1

    message["Data"]["alerts"]["active"][1]["alert"]["isStillActive"] = False
    system.processMessage(message)
    assert system.heatpump_low_ambient_lockout is False
    assert system.aux_heat_high_ambient_lockout is False
    assert len(system.active_alerts) == 0
