"""Pytest fixtures"""
import json
import os
import asyncio
import pytest

from lennoxs30api.metrics import Metrics
from lennoxs30api.s30api_async import s30api_async

def loadfile(name, sys_id=None) -> json:
    """Loads a JSON file from the messages directory"""
    script_dir = os.path.dirname(__file__) + "/messages/"
    file_path = os.path.join(script_dir, name)
    with open(file_path,encoding="utf-8") as f:
        data = json.load(f)
    if sys_id is not None:
        data["SenderID"] = sys_id
    return data


@pytest.fixture
def metrics() -> Metrics:
    """Creates a metrics fixture"""
    return Metrics()


@pytest.fixture
def api() -> s30api_async:
    """Constructs API object and loads it with data."""
    asyncio.set_event_loop(asyncio.new_event_loop())

    api_ret = s30api_async("myemail@email.com", "mypassword", None)
    data = loadfile("login_response.json")
    api_ret.process_login_response(data)

    data = loadfile("config_response_system_01.json")
    api_ret.processMessage(data)

    data = loadfile("config_response_system_02.json")
    api_ret.processMessage(data)

    data = loadfile("config_system_03_heatpump_and_furnace.json")
    api_ret.processMessage(data)

    data = loadfile("equipments_lcc_splitsetpoint.json")
    data["SenderID"] = "0000000-0000-0000-0000-000000000001"
    api_ret.processMessage(data)
    return api_ret

@pytest.fixture
def api_single_setpoint() -> s30api_async:
    """Constructs API object and loads it with data."""
    asyncio.set_event_loop(asyncio.new_event_loop())

    api_ret = s30api_async("myemail@email.com", "mypassword", None)
    data = loadfile("login_response.json")
    api_ret.process_login_response(data)

    data = loadfile("config_response_system_01.json")
    api_ret.processMessage(data)

    data = loadfile("config_response_system_02.json")
    api_ret.processMessage(data)

    data = loadfile("config_system_03_heatpump_and_furnace.json")
    api_ret.processMessage(data)

    data = loadfile("equipments_lcc_singlesetpoint.json")
    data["SenderID"] = "0000000-0000-0000-0000-000000000001"
    api_ret.processMessage(data)
    return api_ret


@pytest.fixture
def api_system_04_furn_ac_zoning() -> s30api_async:
    """Loads the system04 furnace with zoning configuration"""
    asyncio.set_event_loop(asyncio.new_event_loop())
    api_ret = s30api_async("myemail@email.com", "mypassword", None, ip_address="10.0.0.1")
    api_ret.setup_local_homes()

    data = loadfile("system_04_furn_ac_zoning_config.json", "LCC")
    api_ret.processMessage(data)

    data = loadfile("system_04_furn_ac_zoning_equipment.json", "LCC")
    api_ret.processMessage(data)

    data = loadfile("system_04_furn_ac_zoning_devices.json", "LCC")
    api_ret.processMessage(data)

    data = loadfile("system_04_furn_ac_zoning_zones.json", "LCC")
    api_ret.processMessage(data)

    data = loadfile("system_04_furn_ac_zoning_rgw.json", "LCC")
    api_ret.processMessage(data)

    data = loadfile("system_04_furn_ac_zoning_alerts.json", "LCC")
    api_ret.processMessage(data)

    data = loadfile("system_04_furn_ac_zoning_indoorAirQuality.json", "LCC")
    api_ret.processMessage(data)
    return api_ret

@pytest.fixture
def api_device_lcc() -> s30api_async:
    """Fixture for local device response"""
    api_ret = s30api_async("myemail@email.com", "mypassword", None, ip_address="10.0.0.1")
    api_ret.setup_local_homes()

    data = loadfile("device_response_lcc.json")
    api_ret.processMessage(data)
    return api_ret

@pytest.fixture
def api_m30() -> s30api_async:
    """Fixture for m30 thermostat"""
    asyncio.set_event_loop(asyncio.new_event_loop())

    api_ret = s30api_async("myemail@email.com", "mypassword", None)
    data = loadfile("login_response.json")
    api_ret.process_login_response(data)

    data = loadfile("m30_config_response.json")
    api_ret.processMessage(data)

    data = loadfile("m30_device_response.json")
    api_ret.processMessage(data)

    return api_ret
