from lennoxs30api.s30api_async import lennox_zone, s30api_async, lennox_system
from lennoxs30api.lennox_home import lennox_home

import json
import os


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
    data['Data']['equipments'][1]['equipment']['diagnostics'][19]['diagnostic']['value'] = "Open"
    data['Data']['equipments'][1]['equipment']['diagnostics'][20]['diagnostic']['value'] = "Open"
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
    data['Data']['equipments'][1]['equipment']['diagnostics'][19]['diagnostic']['value'] = "Open"
    data['Data']['equipments'][1]['equipment']['diagnostics'][20]['diagnostic']['value'] = "Open"
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
    del data['Data']['equipments'][1]['equipment']['diagnostics'][19]['diagnostic']['name']
    del data['Data']['equipments'][1]['equipment']['diagnostics'][20]['diagnostic']['name']
    del data['Data']['equipments'][0]
    api.processMessage(data)

    assert lsystem.diagInverterInputVoltage == "247.0"
    assert lsystem.diagInverterInputCurrent == "4.301"
    assert dirtyVoltage.triggered == True
    assert dirtyCurrent.triggered == True
