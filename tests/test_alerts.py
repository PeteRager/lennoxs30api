from lennoxs30api.s30api_async import lennox_system

from tests.conftest import loadfile


class DirtySubscription:
    def __init__(self, system: lennox_system, attr_name: str):
        self.triggered: int = 0
        self.id = attr_name
        system.registerOnUpdateCallback(self.update_callback, [attr_name])

    def update_callback(self):
        self.triggered = self.triggered + 1


def test_alerts(api_system_04_furn_ac_zoning):
    api = api_system_04_furn_ac_zoning
    system: lennox_system = api.system_list[0]
    assert system.sysId == "LCC"

    assert system.alerts_num_cleared == 46
    assert system.alerts_num_active == 2
    assert system.alerts_last_cleared_id == 45
    assert system.alerts_num_in_active_array == 2

    assert system.heatpump_low_ambient_lockout == False
    assert system.aux_heat_high_ambient_lockout == True

    alert = system.active_alerts[1]
    assert alert["code"] == 19
    assert alert["userMessageID"] == 0
    assert alert["userMessage"] == ""
    assert alert["isStillActive"] == True
    assert alert["timestampLast"] == "1636473073"
    assert alert["priority"] == "info"
    assert alert["equipmentType"] == 0
    assert alert["message"] == "High Ambient Auxiliary Heat Lockout"
    assert alert["code"] == 19
    assert alert["userMessageID"] == 0
    assert alert["userMessage"] == ""
    assert alert["isStillActive"] == True
    assert alert["timestampLast"] == "1636473073"
    assert alert["priority"] == "info"
    assert alert["equipmentType"] == 0
    assert alert["message"] == "High Ambient Auxiliary Heat Lockout"

    alert = system.active_alerts[0]
    assert alert["code"] == 434
    assert alert["userMessageID"] == 49153
    assert alert["userMessage"] == "Problem"
    assert alert["isStillActive"] == True
    assert alert["timestampLast"] == "1665497389"
    assert alert["priority"] == "moderate"
    assert alert["equipmentType"] == 18
    assert alert["message"] == "OU Inverter Communication Error To Main Control"


def test_alerts_unknown_alert(api_system_04_furn_ac_zoning):
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
    assert alert["isStillActive"] == True
    assert alert["timestampLast"] == "1665497389"
    assert alert["priority"] == "moderate"
    assert alert["equipmentType"] == 18
    assert alert["message"] == "unknown alert code"


def test_alerts_no_active_alerts(api_system_04_furn_ac_zoning):
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
    api = api_system_04_furn_ac_zoning
    system: lennox_system = api.system_list[0]
    assert system.sysId == "LCC"

    message = loadfile("alert_lockouts.json", "LCC")
    system.processMessage(message)

    assert system.heatpump_low_ambient_lockout == False
    assert system.aux_heat_high_ambient_lockout == True
    assert len(system.active_alerts) == 1

    alert = system.active_alerts[0]
    assert alert["code"] == 19
    assert alert["userMessageID"] == 0
    assert alert["userMessage"] == ""
    assert alert["isStillActive"] == True
    assert alert["timestampLast"] == "1636473073"
    assert alert["priority"] == "info"
    assert alert["equipmentType"] == 0
    assert alert["message"] == "High Ambient Auxiliary Heat Lockout"

    message["Data"]["alerts"]["active"][1]["alert"]["isStillActive"] = True
    system.processMessage(message)

    assert system.heatpump_low_ambient_lockout == True
    assert system.aux_heat_high_ambient_lockout == True
    assert len(system.active_alerts) == 2

    alert = system.active_alerts[0]
    assert alert["code"] == 19
    assert alert["userMessageID"] == 0
    assert alert["userMessage"] == ""
    assert alert["isStillActive"] == True
    assert alert["timestampLast"] == "1636473073"
    assert alert["priority"] == "info"
    assert alert["equipmentType"] == 0
    assert alert["message"] == "High Ambient Auxiliary Heat Lockout"

    alert = system.active_alerts[1]
    assert alert["code"] == 18
    assert alert["userMessageID"] == 0
    assert alert["userMessage"] == "Low Ambient HP Heat Lockout"
    assert alert["isStillActive"] == True
    assert alert["timestampLast"] == "1636460248"
    assert alert["priority"] == "info"
    assert alert["equipmentType"] == 0
    assert alert["message"] == "Low Ambient HP Heat Lockout"

    message["Data"]["alerts"]["active"][0]["alert"]["isStillActive"] = False
    system.processMessage(message)
    assert system.heatpump_low_ambient_lockout == True
    assert system.aux_heat_high_ambient_lockout == False
    assert len(system.active_alerts) == 1

    message["Data"]["alerts"]["active"][1]["alert"]["isStillActive"] = False
    system.processMessage(message)
    assert system.heatpump_low_ambient_lockout == False
    assert system.aux_heat_high_ambient_lockout == False
    assert len(system.active_alerts) == 0
