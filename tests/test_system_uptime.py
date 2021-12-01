import logging
from lennoxs30api.s30api_async import s30api_async, lennox_system

import json
import os

from unittest.mock import patch


def loadfile(name) -> json:
    script_dir = os.path.dirname(__file__) + "/messages/"
    file_path = os.path.join(script_dir, name)
    with open(file_path) as f:
        data = json.load(f)
    return data


def setup_load_configuration() -> s30api_async:

    api = s30api_async("myemail@email.com", "mypassword", None)
    data = loadfile("login_response.json")
    api.process_login_response(data)

    data = loadfile("config_response_system_01.json")
    api.processMessage(data)

    data = loadfile("config_response_system_02.json")
    api.processMessage(data)
    return api


def test_system_uptime(caplog):
    api = setup_load_configuration()

    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.sysUpTime == 698820

    with caplog.at_level(logging.WARNING):
        caplog.clear()
        data = loadfile("system_uptime.json")
        api.processMessage(data)
        assert lsystem.sysUpTime == 5039520
        assert len(caplog.records) == 0

        data = loadfile("system_uptime_reset.json")
        api.processMessage(data)
        assert lsystem.sysUpTime == 500
        assert len(caplog.records) == 1
