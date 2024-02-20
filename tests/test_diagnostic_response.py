"""Tests the diagnostic response from the controller"""
import os

from lennoxs30api.lennox_equipment import lennox_equipment, lennox_equipment_diagnostic
from lennoxs30api.s30api_async import s30api_async, lennox_system


from tests.conftest import loadfile

# where device responses can be found
script_dir = os.path.dirname(__file__) + "/messages/"


class DirtySubscription:
    """Subscription mock"""
    def __init__(self, system: lennox_system, attr_name: str):
        self.triggered = False
        system.registerOnUpdateCallback(self.update_callback, [attr_name])

    def update_callback(self):
        """Called when the subscription updates"""
        self.triggered = True

def test_process_equipment_energy(api_device_lcc: s30api_async):
    """Tests processing inverter energy"""
    api = api_device_lcc
    lsystem: lennox_system = api.system_list[0]
    dirty_voltage = DirtySubscription(lsystem, "diagInverterInputVoltage")
    dirty_current = DirtySubscription(lsystem, "diagInverterInputCurrent")
    assert lsystem.diagInverterInputVoltage is None
    assert lsystem.diagInverterInputCurrent is None
    assert dirty_voltage.triggered is False
    assert dirty_current.triggered is False

    data = loadfile("equipments_response_energy.json")
    api.processMessage(data)

    assert lsystem.diagInverterInputVoltage == "247.0"
    assert lsystem.diagInverterInputCurrent == "4.301"
    assert dirty_voltage.triggered is True
    assert dirty_current.triggered is True

    # test that the callback doesn't trigger again for identical values
    dirty_voltage.triggered = False
    dirty_current.triggered = False
    data = loadfile("equipments_response_energy.json")

    assert lsystem.diagInverterInputVoltage == "247.0"
    assert lsystem.diagInverterInputCurrent == "4.301"
    assert dirty_voltage.triggered is False
    assert dirty_current.triggered is False


def test_process_equipment_energy_invalid(api_device_lcc: s30api_async):
    """Test error handling for invalid data"""
    api = api_device_lcc
    lsystem: lennox_system = api.system_list[0]
    dirty_voltage = DirtySubscription(lsystem, "diagInverterInputVoltage")
    dirty_current = DirtySubscription(lsystem, "diagInverterInputCurrent")
    assert lsystem.diagInverterInputVoltage is None
    assert lsystem.diagInverterInputCurrent is None

    data = loadfile("equipments_response_energy.json")
    data["Data"]["equipments"][1]["equipment"]["diagnostics"][19]["diagnostic"][
        "value"
    ] = "Open"
    data["Data"]["equipments"][1]["equipment"]["diagnostics"][20]["diagnostic"][
        "value"
    ] = "Open"
    api.processMessage(data)

    assert lsystem.diagInverterInputVoltage == "Open"
    assert lsystem.diagInverterInputCurrent == "Open"
    assert dirty_voltage.triggered is True
    assert dirty_current.triggered is True


def test_process_equipment_energy_unnamed(api_device_lcc: s30api_async):
    """Tests a variety of error conditions"""
    api = api_device_lcc
    lsystem: lennox_system = api.system_list[0]
    dirty_voltage = DirtySubscription(lsystem, "diagInverterInputVoltage")
    dirty_current = DirtySubscription(lsystem, "diagInverterInputCurrent")
    assert lsystem.diagInverterInputVoltage is None
    assert lsystem.diagInverterInputCurrent is None

    # load up empty diagnostics
    data = loadfile("equipments_response_energy.json")
    data["Data"]["equipments"][1]["equipment"]["diagnostics"][19]["diagnostic"][
        "value"
    ] = "Open"
    data["Data"]["equipments"][1]["equipment"]["diagnostics"][20]["diagnostic"][
        "value"
    ] = "Open"
    api.processMessage(data)

    assert lsystem.diagInverterInputVoltage == "Open"
    assert lsystem.diagInverterInputCurrent == "Open"
    assert dirty_voltage.triggered is True
    assert dirty_current.triggered is True

    # new diagnostic update is missing names and an earlier equipment
    dirty_voltage.triggered = False
    dirty_current.triggered = False
    data = loadfile("equipments_response_energy.json")
    del data["Data"]["equipments"][1]["equipment"]["diagnostics"][19]["diagnostic"][
        "name"
    ]
    del data["Data"]["equipments"][1]["equipment"]["diagnostics"][20]["diagnostic"][
        "name"
    ]
    del data["Data"]["equipments"][0]
    api.processMessage(data)

    assert lsystem.diagInverterInputVoltage == "247.0"
    assert lsystem.diagInverterInputCurrent == "4.301"
    assert dirty_voltage.triggered is True
    assert dirty_current.triggered is True


def test_process_diagnostics(api_device_lcc: s30api_async):
    """Test loading the diagnostic entries"""
    api = api_device_lcc
    lsystem: lennox_system = api.system_list[0]
    assert len(lsystem.diagnosticPaths) == 0
    assert len(lsystem.equipment) == 0

    data = loadfile("equipments_response_energy.json")
    api.processMessage(data)

    # It appears that only the power inverted diagnostics are captured in here
    # and the other diagnostics are not stored and only provided via callbacks.
    assert len(lsystem.diagnosticPaths) == 2
    assert len(lsystem.equipment) == 3

    assert len(lsystem.equipment[0].diagnostics) == 1
    assert len(lsystem.equipment[1].diagnostics) == 23
    assert len(lsystem.equipment[2].diagnostics) == 24

    eq1: lennox_equipment = lsystem.equipment[1]
    assert len(eq1.diagnostics) == 23

    eq_did: lennox_equipment_diagnostic = eq1.diagnostics[0]
    assert eq_did.name == "Comp. Short Cycle Delay Active"
    assert eq_did.unit == ""
    assert eq_did.value == "No"

    eq_did: lennox_equipment_diagnostic = eq1.diagnostics[1]
    assert eq_did.name == "Cooling Rate"
    assert eq_did.unit == "%"
    assert eq_did.value == "0.0"

    eq_did: lennox_equipment_diagnostic = eq1.diagnostics[2]
    assert eq_did.name == "Heating Rate"
    assert eq_did.unit == "%"
    assert eq_did.value == "0.0"

    eq_did: lennox_equipment_diagnostic = eq1.diagnostics[3]
    assert eq_did.name == "Compressor Shift Delay Active"
    assert eq_did.unit == ""
    assert eq_did.value == "No"

    eq_did: lennox_equipment_diagnostic = eq1.diagnostics[4]
    assert eq_did.name == "Defrost Status"
    assert eq_did.unit == ""
    assert eq_did.value == "Off"

    eq_did: lennox_equipment_diagnostic = eq1.diagnostics[9]
    assert eq_did.name == "Liquid Line Temp"
    assert eq_did.unit == "F"
    assert eq_did.value == "64.3"

    eq_did: lennox_equipment_diagnostic = eq1.diagnostics[22]
    assert eq_did.name == "Compressor Current"
    assert eq_did.unit == "A"
    assert eq_did.value == "0.000"

    #### Repeat for equipment 2


class DirtyDiagnosticsSubscription:
    """Mock for testing diagnostic subscriptions"""
    def __init__(self, system: lennox_system, eid_did: str):
        self.trigger_count: int = 0
        self.eid_did: str = None
        self.value: str = None
        system.registerOnUpdateCallbackDiag(self.update_callback, eid_did)

    def update_callback(self, eid_did: str, value: str):
        """Callback for diagnostic update"""
        self.trigger_count += 1
        self.eid_did = eid_did
        self.value = value

    def clear(self):
        """Reset the mock"""
        self.trigger_count: int = 0
        self.eid_did: str = None
        self.value: str = None


def test_diagnostics_subscription(api_device_lcc: s30api_async):
    """Tests the diagnostic subscription"""
    api = api_device_lcc
    lsystem: lennox_system = api.system_list[0]
    assert len(lsystem.diagnosticPaths) == 0
    assert len(lsystem.equipment) == 0

    message = loadfile("equipments_response_energy.json")
    api.processMessage(message)

    sub1 = DirtyDiagnosticsSubscription(lsystem, ["1_0"])
    sub2 = DirtyDiagnosticsSubscription(lsystem, ["1_1"])
    sub3 = DirtyDiagnosticsSubscription(lsystem, ["1_0", "1_1"])
    assert sub1.trigger_count == 0
    assert sub2.trigger_count == 0
    assert sub3.trigger_count == 0
    message = loadfile("equipments_diag_update.json")
    api.processMessage(message)

    assert sub1.trigger_count == 1
    assert sub1.eid_did == "1_0"
    assert sub1.value == "Yes"
    assert lsystem.equipment[1].diagnostics[0].value == "Yes"

    assert sub2.trigger_count == 1
    assert sub2.eid_did == "1_1"
    assert sub2.value == "10.0"
    assert lsystem.equipment[1].diagnostics[1].value == "10.0"

    assert sub3.trigger_count == 2

    # Process the same file again, should result in no changes and no callbacks
    sub1.clear()
    sub2.clear()
    sub3.clear()
    assert sub1.trigger_count == 0
    assert sub2.trigger_count == 0
    message = loadfile("equipments_diag_update.json")
    api.processMessage(message)

    assert sub1.trigger_count == 0
    assert sub1.eid_did is None
    assert sub1.value is None
    assert lsystem.equipment[1].diagnostics[0].value == "Yes"

    assert sub2.trigger_count == 0
    assert sub2.eid_did is None
    assert sub2.value is None
    assert lsystem.equipment[1].diagnostics[1].value == "10.0"

    assert sub3.trigger_count == 0

    message["Data"]["equipments"][0]["equipment"]["diagnostics"][0]["diagnostic"][
        "value"
    ] = "No"
    api.processMessage(message)
    assert sub1.trigger_count == 1
    assert sub1.eid_did == "1_0"
    assert sub1.value == "No"
    assert lsystem.equipment[1].diagnostics[0].value == "No"

    assert sub2.trigger_count == 0
    assert sub2.eid_did is None
    assert sub2.value is None
    assert lsystem.equipment[1].diagnostics[1].value == "10.0"

    assert sub3.trigger_count == 1

    sub1.clear()
    sub3.clear()
    assert sub1.trigger_count == 0
    message["Data"]["equipments"][0]["equipment"]["diagnostics"][1]["diagnostic"][
        "value"
    ] = "11.1"
    api.processMessage(message)
    assert sub1.trigger_count == 0
    assert sub1.eid_did is None
    assert sub1.value is None
    assert sub2.trigger_count == 1
    assert sub2.eid_did == "1_1"
    assert sub2.value == "11.1"
    assert sub3.trigger_count == 1
    assert lsystem.equipment[1].diagnostics[1].value == "11.1"
