from lennoxs30api.s30api_async import lennox_zone, s30api_async, lennox_system
from lennoxs30api.lennox_home import lennox_home

import json
import os


def setup_load_configuration() -> s30api_async:
    script_dir = os.path.dirname(__file__) + "/messages/"
    file_path = os.path.join(script_dir, "login_response.json")
    with open(file_path) as f:
        data = json.load(f)

    api = s30api_async("myemail@email.com", "mypassword", None)
    api.process_login_response(data)

    file_path = os.path.join(script_dir, "config_response_system_01.json")
    with open(file_path) as f:
        data = json.load(f)
    api.processMessage(data)

    file_path = os.path.join(script_dir, "config_response_system_02.json")
    with open(file_path) as f:
        data = json.load(f)
    api.processMessage(data)
    return api


def test_celsius_round():
    api = setup_load_configuration()

    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"

    assert lsystem.celsius_round(20.7) == 20.5
    assert lsystem.celsius_round(20.0) == 20.0
    assert lsystem.celsius_round(20.8) == 21.0


def test_faren_round():
    api = setup_load_configuration()

    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"

    assert lsystem.faren_round(75.0) == 75
    assert lsystem.faren_round(75.4) == 75
    assert lsystem.faren_round(75.6) == 76
