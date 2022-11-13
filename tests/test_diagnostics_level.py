from lennoxs30api.s30api_async import (
    LENNOX_HVAC_EMERGENCY_HEAT,
    lennox_zone,
    lennox_system,
    s30api_async,
)

import json
import asyncio
import os

from unittest.mock import patch

from lennoxs30api.s30exception import EC_BAD_PARAMETERS, S30Exception


def loadfile(name) -> json:
    script_dir = os.path.dirname(__file__) + "/messages/"
    file_path = os.path.join(script_dir, name)
    with open(file_path) as f:
        data = json.load(f)
    return data


def test_get_diagnostic_level(api: s30api_async):
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.diagLevel == None

    message = loadfile("systemControl_diag_level_0.json")
    message["SenderID"] = lsystem.sysId
    api.processMessage(message)
    assert lsystem.diagLevel == 0

    message = loadfile("systemControl_diag_level_1.json")
    message["SenderID"] = lsystem.sysId
    api.processMessage(message)
    assert lsystem.diagLevel == 1
