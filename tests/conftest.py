from lennoxs30api.metrics import Metrics
from lennoxs30api.s30api_async import (
    LENNOX_HVAC_EMERGENCY_HEAT,
    lennox_zone,
    s30api_async,
    lennox_system,
)

import json
import os
import asyncio
import pytest

from unittest.mock import patch

from lennoxs30api.s30exception import S30Exception


def loadfile(name, sysId=None) -> json:
    script_dir = os.path.dirname(__file__) + "/messages/"
    file_path = os.path.join(script_dir, name)
    with open(file_path) as f:
        data = json.load(f)
    if sysId != None:
        data["SenderID"] = sysId
    return data


@pytest.fixture
def metrics() -> Metrics:
    return Metrics()


@pytest.fixture
def api(single_setpoint: bool = False) -> s30api_async:
    asyncio.set_event_loop(asyncio.new_event_loop())

    api = s30api_async("myemail@email.com", "mypassword", None)
    data = loadfile("login_response.json")
    api.process_login_response(data)

    data = loadfile("config_response_system_01.json")
    api.processMessage(data)

    data = loadfile("config_response_system_02.json")
    api.processMessage(data)

    data = loadfile("config_system_03_heatpump_and_furnace.json")
    api.processMessage(data)

    if single_setpoint == True:
        data = loadfile("equipments_lcc_singlesetpoint.json")
        data["SenderID"] = "0000000-0000-0000-0000-000000000001"
    else:
        data = loadfile("equipments_lcc_splitsetpoint.json")
        data["SenderID"] = "0000000-0000-0000-0000-000000000001"
    api.processMessage(data)

    return api


@pytest.fixture
def api_system_04_furn_ac_zoning() -> s30api_async:
    asyncio.set_event_loop(asyncio.new_event_loop())
    api = s30api_async("myemail@email.com", "mypassword", None, ip_address="10.0.0.1")
    api.setup_local_homes()

    data = loadfile("system_04_furn_ac_zoning_config.json", "LCC")
    api.processMessage(data)

    data = loadfile("system_04_furn_ac_zoning_equipment.json", "LCC")
    api.processMessage(data)

    return api
