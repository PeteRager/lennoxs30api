from lennoxs30api.s30api_async import (
    LENNOX_ALERT_MINOR,
    LENNOX_ALERT_NONE,
    LENNOX_DEHUMIDIFICATION_MODE_AUTO,
    LENNOX_HUMIDIFICATION_MODE_BASIC,
    LENNOX_HVAC_COOL,
    LENNOX_HVAC_HEAT,
    LENNOX_HVAC_HEAT_COOL,
    LENNOX_HVAC_OFF,
    LENNOX_NONE_STR,
    LENNOX_SA_SETPOINT_STATE_HOME,
    LENNOX_SA_SETPOINT_STATE_AWAY,
    LENNOX_SA_SETPOINT_STATE_TRANSITION,
    LENNOX_SA_STATE_DISABLED,
    LENNOX_SA_STATE_ENABLED_CANCELLED,
    LENNOX_STATUS_GOOD,
    LENNOX_ZONING_MODE_CENTRAL,
    LENNOX_ZONING_MODE_ZONED,
    lennox_zone,
    s30api_async,
    lennox_system,
)
from lennoxs30api.lennox_home import lennox_home

import json
import os
import pytest

from tests.conftest import loadfile


def test_alerts(api_system_04_furn_ac_zoning):
    api = api_system_04_furn_ac_zoning
    system: lennox_system = api.getSystems()[0]
    assert system.sysId == "LCC"

    assert system.alerts_num_cleared == 46
    assert system.alerts_num_active == 1
    assert system.alerts_last_cleared_id == 45
    assert system.alerts_num_in_active_array == 1

    alert = system.active_alerts[0]
    assert alert["id"] == 0
    assert alert["alert"]["code"] == 434
    assert alert["alert"]["userMessageID"] == 49153
    assert alert["alert"]["userMessage"] == "Problem"
    assert alert["alert"]["isStillActive"] == True
    assert alert["alert"]["timestampLast"] == "1665497389"
    assert alert["alert"]["priority"] == "moderate"
    assert alert["alert"]["equipmentType"] == 18
    assert (
        alert["alert"]["message"] == "OU Inverter Communication Error To Main Control"
    )


def test_alerts_unknown_alert(api_system_04_furn_ac_zoning):
    api = api_system_04_furn_ac_zoning
    system: lennox_system = api.getSystems()[0]
    assert system.sysId == "LCC"

    message = loadfile("system_04_furn_ac_zoning_alerts.json", "LCC")
    message["Data"]["alerts"]["active"][0]["alert"]["code"] = 998
    system.processMessage(message)

    assert system.alerts_num_cleared == 46
    assert system.alerts_num_active == 1
    assert system.alerts_last_cleared_id == 45
    assert system.alerts_num_in_active_array == 1

    alert = system.active_alerts[0]
    assert alert["id"] == 0
    assert alert["alert"]["code"] == 998
    assert alert["alert"]["userMessageID"] == 49153
    assert alert["alert"]["userMessage"] == "Problem"
    assert alert["alert"]["isStillActive"] == True
    assert alert["alert"]["timestampLast"] == "1665497389"
    assert alert["alert"]["priority"] == "moderate"
    assert alert["alert"]["equipmentType"] == 18
    assert alert["alert"]["message"] == "unknown alert code"


def test_alerts_no_active_alerts(api_system_04_furn_ac_zoning):
    api = api_system_04_furn_ac_zoning
    system: lennox_system = api.getSystems()[0]
    assert system.sysId == "LCC"

    message = loadfile("system_04_furn_ac_zoning_alerts.json", "LCC")
    message["Data"]["alerts"].pop("active")
    message["Data"]["alerts"]["meta"]["numAlertsInActiveArray"] = 0

    system.processMessage(message)

    assert system.alerts_num_cleared == 46
    assert system.alerts_num_active == 1
    assert system.alerts_last_cleared_id == 45
    assert system.alerts_num_in_active_array == 0

    assert len(system.active_alerts) == 0


# An alert code of zero indicates no alert.
def test_alerts_alert_code_0(api_system_04_furn_ac_zoning):
    api = api_system_04_furn_ac_zoning
    system: lennox_system = api.getSystems()[0]
    assert system.sysId == "LCC"

    message = loadfile("system_04_furn_ac_zoning_alerts.json", "LCC")
    message["Data"]["alerts"]["active"][0]["alert"]["code"] = 0
    system.processMessage(message)

    assert len(system.active_alerts) == 0
