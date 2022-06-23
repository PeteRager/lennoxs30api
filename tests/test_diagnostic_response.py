from lennoxs30api.lennox_equipment import lennox_equipment, lennox_equipment_diagnostic
from lennoxs30api.s30api_async import lennox_zone, s30api_async, lennox_system
from lennoxs30api.lennox_home import lennox_home

import json
import os

from tests.conftest import loadfile


# where device responses can be found
script_dir = os.path.dirname(__file__) + "/messages/"


class DirtySubscription:
    def __init__(self, system: lennox_system, attr_name: str):
        self.triggered = False
        system.registerOnUpdateCallback(self.update_callback, [attr_name])

    def update_callback(self):
        self.triggered = True


def setup_load_configuration() -> s30api_async:
    api = s30api_async("myemail@email.com", "mypassword", None, ip_address="10.0.0.1")
    api.setup_local_homes()

    file_path = os.path.join(script_dir, "device_response_lcc.json")
    with open(file_path) as f:
        data = json.load(f)
    api.processMessage(data)

    return api


def test_process_equipment_energy():
    api = setup_load_configuration()
    lsystem: lennox_system = api.getSystems()[0]
    dirtyVoltage = DirtySubscription(lsystem, "diagInverterInputVoltage")
    dirtyCurrent = DirtySubscription(lsystem, "diagInverterInputCurrent")
    assert lsystem.diagInverterInputVoltage == None
    assert lsystem.diagInverterInputCurrent == None
    assert dirtyVoltage.triggered == False
    assert dirtyCurrent.triggered == False

    file_path = os.path.join(script_dir, "equipments_response_energy.json")
    with open(file_path) as f:
        data = json.load(f)
    api.processMessage(data)

    assert lsystem.diagInverterInputVoltage == "247.0"
    assert lsystem.diagInverterInputCurrent == "4.301"
    assert dirtyVoltage.triggered == True
    assert dirtyCurrent.triggered == True

    # test that the callback doesn't trigger again for identical values
    dirtyVoltage.triggered = False
    dirtyCurrent.triggered = False
    file_path = os.path.join(script_dir, "equipments_response_energy.json")
    with open(file_path) as f:
        data = json.load(f)
    api.processMessage(data)

    assert lsystem.diagInverterInputVoltage == "247.0"
    assert lsystem.diagInverterInputCurrent == "4.301"
    assert dirtyVoltage.triggered == False
    assert dirtyCurrent.triggered == False


def test_process_equipment_energy_invalid():
    api = setup_load_configuration()
    lsystem: lennox_system = api.getSystems()[0]
    dirtyVoltage = DirtySubscription(lsystem, "diagInverterInputVoltage")
    dirtyCurrent = DirtySubscription(lsystem, "diagInverterInputCurrent")
    assert lsystem.diagInverterInputVoltage == None
    assert lsystem.diagInverterInputCurrent == None

    file_path = os.path.join(script_dir, "equipments_response_energy.json")
    with open(file_path) as f:
        data = json.load(f)
    data["Data"]["equipments"][1]["equipment"]["diagnostics"][19]["diagnostic"][
        "value"
    ] = "Open"
    data["Data"]["equipments"][1]["equipment"]["diagnostics"][20]["diagnostic"][
        "value"
    ] = "Open"
    api.processMessage(data)

    assert lsystem.diagInverterInputVoltage == "Open"
    assert lsystem.diagInverterInputCurrent == "Open"
    assert dirtyVoltage.triggered == True
    assert dirtyCurrent.triggered == True


def test_process_equipment_energy_unnamed():
    api = setup_load_configuration()
    lsystem: lennox_system = api.getSystems()[0]
    dirtyVoltage = DirtySubscription(lsystem, "diagInverterInputVoltage")
    dirtyCurrent = DirtySubscription(lsystem, "diagInverterInputCurrent")
    assert lsystem.diagInverterInputVoltage == None
    assert lsystem.diagInverterInputCurrent == None

    # load up empty diagnostics
    file_path = os.path.join(script_dir, "equipments_response_energy.json")
    with open(file_path) as f:
        data = json.load(f)
    data["Data"]["equipments"][1]["equipment"]["diagnostics"][19]["diagnostic"][
        "value"
    ] = "Open"
    data["Data"]["equipments"][1]["equipment"]["diagnostics"][20]["diagnostic"][
        "value"
    ] = "Open"
    api.processMessage(data)

    assert lsystem.diagInverterInputVoltage == "Open"
    assert lsystem.diagInverterInputCurrent == "Open"
    assert dirtyVoltage.triggered == True
    assert dirtyCurrent.triggered == True

    # new diagnostic update is missing names and an earlier equipment
    dirtyVoltage.triggered = False
    dirtyCurrent.triggered = False
    file_path = os.path.join(script_dir, "equipments_response_energy.json")
    with open(file_path) as f:
        data = json.load(f)
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
    assert dirtyVoltage.triggered == True
    assert dirtyCurrent.triggered == True


def test_process_diagnostics():
    api = setup_load_configuration()
    lsystem: lennox_system = api.getSystems()[0]
    assert len(lsystem.diagnosticPaths) == 0
    assert len(lsystem.equipment) == 0

    file_path = os.path.join(script_dir, "equipments_response_energy.json")
    with open(file_path) as f:
        data = json.load(f)
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
    def __init__(self, system: lennox_system, eid_did: str):
        self.trigger_count: int = 0
        self.eid_did: str = None
        self.value: str = None
        system.registerOnUpdateCallbackDiag(self.update_callback, eid_did)

    def update_callback(self, eid_did: str, value: str):
        self.trigger_count += 1
        self.eid_did = eid_did
        self.value = value

    def clear(self):
        self.trigger_count: int = 0
        self.eid_did: str = None
        self.value: str = None


def test_diagnostics_subscription():
    api = setup_load_configuration()
    lsystem: lennox_system = api.getSystems()[0]
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
    assert sub1.eid_did == None
    assert sub1.value == None
    assert lsystem.equipment[1].diagnostics[0].value == "Yes"

    assert sub2.trigger_count == 0
    assert sub2.eid_did == None
    assert sub2.value == None
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
    assert sub2.eid_did == None
    assert sub2.value == None
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
    assert sub1.eid_did == None
    assert sub1.value == None
    assert sub2.trigger_count == 1
    assert sub2.eid_did == "1_1"
    assert sub2.value == "11.1"
    assert sub3.trigger_count == 1
    assert lsystem.equipment[1].diagnostics[1].value == "11.1"
