from lennoxs30api.s30api_async import lennox_zone, s30api_async, lennox_system
from lennoxs30api.lennox_home import lennox_home

import json
import os


def setup_load_lcc_configuration() -> s30api_async:
    script_dir = os.path.dirname(__file__) + "/messages/"

    api = s30api_async("myemail@email.com", "mypassword", None, ip_address="10.0.0.1")
    api.setup_local_homes()

    file_path = os.path.join(script_dir, "device_response_lcc.json")
    with open(file_path) as f:
        data = json.load(f)
    api.processMessage(data)

    return api


def test_process_device_serial_number():
    api = setup_load_lcc_configuration()

    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "LCC"
    assert lsystem.serialNumber == "HD21212121"
    assert lsystem.unique_id() == "HD21212121"
    assert lsystem.softwareVersion == "3.81.207"
