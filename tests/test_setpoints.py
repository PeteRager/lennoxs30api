from lennoxs30api.s30api_async import lennox_zone, s30api_async, lennox_system
from lennoxs30api.lennox_home import lennox_home

import json
import os
import unittest
import asyncio

from unittest.mock import patch


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


def test_hsp_f():
    api = setup_load_configuration()
    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(zone.setHeatSPF(71))
        loop.close()
        mock_message_helper.assert_called_once()
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        tSchedule = jsbody["Data"]["schedules"][0]
        assert tSchedule["id"] == zone.getManualModeScheduleId()
        tPeriod = tSchedule["schedule"]["periods"][0]["period"]
        assert tPeriod["hsp"] == 71
        assert tPeriod["hspC"] == 21.5
        schedule = lsystem.getSchedule(zone.getManualModeScheduleId())
        zperiod = schedule.getPeriod(0)

        assert tPeriod["csp"] == zperiod.csp
        assert tPeriod["cspC"] == zperiod.cspC


def test_hsp_c():
    api = setup_load_configuration()
    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(zone.setHeatSPC(21.5))
        loop.close()
        mock_message_helper.assert_called_once()
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        tSchedule = jsbody["Data"]["schedules"][0]
        assert tSchedule["id"] == zone.getManualModeScheduleId()
        tPeriod = tSchedule["schedule"]["periods"][0]["period"]
        assert tPeriod["hsp"] == 71
        assert tPeriod["hspC"] == 21.5
        schedule = lsystem.getSchedule(zone.getManualModeScheduleId())
        zperiod = schedule.getPeriod(0)

        assert tPeriod["csp"] == zperiod.csp
        assert tPeriod["cspC"] == zperiod.cspC


def test_csp_f():
    api = setup_load_configuration()
    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(zone.setCoolSPF(73))
        loop.close()
        mock_message_helper.assert_called_once()
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        tSchedule = jsbody["Data"]["schedules"][0]
        assert tSchedule["id"] == zone.getManualModeScheduleId()
        tPeriod = tSchedule["schedule"]["periods"][0]["period"]
        assert tPeriod["csp"] == 73
        assert tPeriod["cspC"] == 23
        schedule = lsystem.getSchedule(zone.getManualModeScheduleId())
        zperiod = schedule.getPeriod(0)

        assert tPeriod["hsp"] == zperiod.hsp
        assert tPeriod["hspC"] == zperiod.hspC


def test_sp_f():
    api = setup_load_configuration()
    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(zone.setHeatCoolSPF(64, 78))
        loop.close()
        mock_message_helper.assert_called_once()
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        tSchedule = jsbody["Data"]["schedules"][0]
        assert tSchedule["id"] == zone.getManualModeScheduleId()
        tPeriod = tSchedule["schedule"]["periods"][0]["period"]
        assert tPeriod["csp"] == 78
        assert tPeriod["cspC"] == 25.5
        assert tPeriod["hsp"] == 64
        assert tPeriod["hspC"] == 18


def test_sp_c():
    api = setup_load_configuration()
    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(zone.setHeatCoolSPC(18, 25.5))
        loop.close()
        mock_message_helper.assert_called_once()
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        tSchedule = jsbody["Data"]["schedules"][0]
        assert tSchedule["id"] == zone.getManualModeScheduleId()
        tPeriod = tSchedule["schedule"]["periods"][0]["period"]
        assert tPeriod["csp"] == 78
        assert tPeriod["cspC"] == 25.5
        assert tPeriod["hsp"] == 64
        assert tPeriod["hspC"] == 18
