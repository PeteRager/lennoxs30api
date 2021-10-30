from lennoxs30api.s30api_async import lennox_zone, s30api_async, lennox_system
from lennoxs30api.lennox_home import lennox_home

import json
import os


def loadfile(name) -> json:
    script_dir = os.path.dirname(__file__) + "/messages/"
    file_path = os.path.join(script_dir, name)
    with open(file_path) as f:
        data = json.load(f)
    return data


def setup_load_lcc_configuration() -> s30api_async:
    api = s30api_async("myemail@email.com", "mypassword", None, ip_address="10.0.0.1")
    api.setup_local_homes()
    return api


def test_process_splitsetpoint():
    api = setup_load_lcc_configuration()
    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "LCC"

    data = loadfile("equipments_lcc_singlesetpoint.json")
    api.processMessage(data)

    assert lsystem.single_setpoint_mode == True

    data = loadfile("equipments_lcc_splitsetpoint.json")
    api.processMessage(data)

    assert lsystem.single_setpoint_mode == False
