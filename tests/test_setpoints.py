from unittest import mock
from lennoxs30api.s30api_async import lennox_zone, s30api_async, lennox_system
from lennoxs30api.lennox_home import lennox_home

import json
import os
import unittest
import asyncio

from unittest.mock import patch


def loadfile(name) -> json:
    script_dir = os.path.dirname(__file__) + "/messages/"
    file_path = os.path.join(script_dir, name)
    with open(file_path) as f:
        data = json.load(f)
    return data


def setup_load_configuration(single_setpoint: bool = False) -> s30api_async:
    asyncio.set_event_loop(asyncio.new_event_loop())

    api = s30api_async("myemail@email.com", "mypassword", None)
    data = loadfile("login_response.json")
    api.process_login_response(data)

    data = loadfile("config_response_system_01.json")
    api.processMessage(data)

    data = loadfile("config_response_system_02.json")
    api.processMessage(data)

    data = loadfile("config_response_system_02.json")
    api.processMessage(data)

    if single_setpoint == True:
        data = loadfile("equipments_lcc_singlesetpoint.json")
        data["SenderID"] = "0000000-0000-0000-0000-000000000001"
    else:
        data = loadfile("equipments_lcc_splitsetpoint.json")
        data["SenderID"] = "0000000-0000-0000-0000-000000000001"
    api.processMessage(data)

    return api


def test_hsp_f():
    api = setup_load_configuration()
    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.single_setpoint_mode == False
    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(zone.perform_setpoint(r_hsp=71))
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
    assert lsystem.single_setpoint_mode == False
    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(zone.perform_setpoint(r_hspC=21.5))
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
    assert lsystem.single_setpoint_mode == False
    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(zone.perform_setpoint(r_csp=73))
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


def test_csp_c():
    api = setup_load_configuration()
    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.single_setpoint_mode == False
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(zone.perform_setpoint(r_cspC=23))
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


def test_hcsp_f():
    api = setup_load_configuration()
    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.single_setpoint_mode == False

    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(zone.perform_setpoint(r_hsp=64, r_csp=78))
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
        assert len(tPeriod) == 4


def test_hcsp_c():
    api = setup_load_configuration()
    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.single_setpoint_mode == False

    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(zone.perform_setpoint(r_hspC=18, r_cspC=25.5))
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
        assert len(tPeriod) == 4


def test_sp_f():
    api = setup_load_configuration(single_setpoint=True)
    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.single_setpoint_mode == True
    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(zone.perform_setpoint(r_sp=78))
        loop.close()
        mock_message_helper.assert_called_once()
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        tSchedule = jsbody["Data"]["schedules"][0]
        assert tSchedule["id"] == zone.getManualModeScheduleId()
        tPeriod = tSchedule["schedule"]["periods"][0]["period"]
        assert tPeriod["sp"] == 78
        assert tPeriod["spC"] == 25.5
        assert len(tPeriod) == 2


def test_sp_c():
    api = setup_load_configuration(True)
    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.single_setpoint_mode == True
    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(zone.perform_setpoint(r_spC=25.5))
        loop.close()
        mock_message_helper.assert_called_once()
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        tSchedule = jsbody["Data"]["schedules"][0]
        assert tSchedule["id"] == zone.getManualModeScheduleId()
        tPeriod = tSchedule["schedule"]["periods"][0]["period"]
        assert tPeriod["sp"] == 78
        assert tPeriod["spC"] == 25.5
        assert len(tPeriod) == 2


def test_override():
    api = setup_load_configuration()
    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.single_setpoint_mode == False
    zone: lennox_zone = lsystem.getZone(0)
    # In the default config all zones are in manual mode, here we fake it to follow the "summer" scheduled
    # such that an override schedule will need to be created.
    zone.scheduleId = 1
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(zone.perform_setpoint(r_hsp=71))
        assert mock_message_helper.call_count == 2

        # First message should be the configuration of the schedule override
        m1 = mock_message_helper.call_args_list[0]
        sysId = m1.args[0]
        message = m1.args[1]
        assert sysId == lsystem.sysId
        jsbody = json.loads("{" + message + "}")

        tSchedule = jsbody["Data"]["schedules"][0]
        assert tSchedule["id"] == zone.getOverrideScheduleId()
        tPeriod = tSchedule["schedule"]["periods"][0]["period"]
        assert tPeriod["hsp"] == 71
        assert tPeriod["hspC"] == 21.5
        assert tPeriod["desp"] == zone.desp
        assert tPeriod["cspC"] == zone.cspC
        assert tPeriod["csp"] == zone.csp
        assert tPeriod["sp"] == zone.sp
        assert tPeriod["husp"] == zone.husp
        assert tPeriod["humidityMode"] == zone.humidityMode
        assert tPeriod["systemMode"] == zone.systemMode
        assert tPeriod["spC"] == zone.spC
        assert tPeriod["startTime"] == zone.startTime
        assert tPeriod["fanMode"] == zone.fanMode

        # Second message should set the zone to follow this schedule
        m2 = mock_message_helper.call_args_list[1]
        sysId = m2.args[0]
        message = m2.args[1]
        assert sysId == lsystem.sysId
        jsbody = json.loads("{" + message + "}")

        tZone = jsbody["Data"]["zones"][0]
        assert tZone["id"] == zone.id
        hold = tZone["config"]["scheduleHold"]
        assert hold["scheduleId"] == zone.getOverrideScheduleId()
        assert hold["exceptionType"] == "hold"
        assert hold["enabled"] == True
        assert hold["expiresOn"] == "0"
        assert hold["expirationMode"] == "nextPeriod"
        assert len(hold) == 5

    # Test a setpoint when the zone is already override
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        # Fake the zone to think it is in override mode.
        zone.scheduleId = zone.getOverrideScheduleId()
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(zone.perform_setpoint(r_csp=75))
        loop.close()
        assert mock_message_helper.call_count == 1

        m1 = mock_message_helper.call_args_list[0]
        sysId = m1.args[0]
        message = m1.args[1]
        assert sysId == lsystem.sysId
        jsbody = json.loads("{" + message + "}")
        tSchedule = jsbody["Data"]["schedules"][0]
        assert tSchedule["id"] == zone.getOverrideScheduleId()
        tPeriod = tSchedule["schedule"]["periods"][0]["period"]
        assert tPeriod["csp"] == 75
        assert tPeriod["cspC"] == 24
        assert tPeriod["hsp"] == zone.hsp
        assert tPeriod["hspC"] == zone.hspC
        assert len(tPeriod) == 4
