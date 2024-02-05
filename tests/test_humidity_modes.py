"""Tests humidty mod"""
import json
import asyncio
from unittest.mock import patch
from lennoxs30api import s30api_async
from lennoxs30api.s30api_async import (
    LENNOX_HUMIDITY_MODE_DEHUMIDIFY,
    LENNOX_HUMIDITY_MODE_HUMIDIFY,
    LENNOX_HUMIDITY_MODE_OFF,
    lennox_zone,
    lennox_system,
)

from lennoxs30api.s30exception import EC_BAD_PARAMETERS, S30Exception

def test_set_humidity_mode_humidify(api: s30api_async):
    """Test setting the humidity mode"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    zone: lennox_zone = lsystem.getZone(0)
    zone.humidificationOption = False
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            _ = loop.run_until_complete(
                zone.setHumidityMode(LENNOX_HUMIDITY_MODE_HUMIDIFY)
            )
        except S30Exception as e:
            ex = e
        assert ex is not None
        assert ex.error_code == EC_BAD_PARAMETERS
        assert mock_message_helper.call_count == 0

    zone.humidificationOption = True
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        _ = loop.run_until_complete(
            zone.setHumidityMode(LENNOX_HUMIDITY_MODE_HUMIDIFY)
        )
        assert mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        t_schedule = jsbody["Data"]["schedules"][0]
        assert t_schedule["id"] == zone.getManualModeScheduleId()
        t_period = t_schedule["schedule"]["periods"][0]["period"]
        assert t_period["humidityMode"] == LENNOX_HUMIDITY_MODE_HUMIDIFY
        assert len(t_period) == 1


def test_set_humidity_mode_dehumidify(api):
    """Test setting dehumidification mode"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    zone: lennox_zone = lsystem.getZone(0)
    zone.dehumidificationOption = False
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            _ = loop.run_until_complete(
                zone.setHumidityMode(LENNOX_HUMIDITY_MODE_DEHUMIDIFY)
            )
        except S30Exception as e:
            ex = e
        assert ex is not None
        assert ex.error_code == EC_BAD_PARAMETERS
        assert mock_message_helper.call_count == 0

    zone.dehumidificationOption = True
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        _ = loop.run_until_complete(
            zone.setHumidityMode(LENNOX_HUMIDITY_MODE_DEHUMIDIFY)
        )
        assert mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        t_schedule = jsbody["Data"]["schedules"][0]
        assert t_schedule["id"] == zone.getManualModeScheduleId()
        t_period = t_schedule["schedule"]["periods"][0]["period"]
        assert t_period["humidityMode"] == LENNOX_HUMIDITY_MODE_DEHUMIDIFY
        assert len(t_period) == 1


def test_set_humidity_mode_off(api):
    """Test setting humidity mode to off"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        _ = loop.run_until_complete(zone.setHumidityMode(LENNOX_HUMIDITY_MODE_OFF))
        assert mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        t_schedule = jsbody["Data"]["schedules"][0]
        assert t_schedule["id"] == zone.getManualModeScheduleId()
        t_period = t_schedule["schedule"]["periods"][0]["period"]
        assert t_period["humidityMode"] == LENNOX_HUMIDITY_MODE_OFF
        assert len(t_period) == 1


def test_set_humidity_mode_bad_mode(api):
    """Test error handling when setting a bad mode"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    zone: lennox_zone = lsystem.getZone(0)
    zone.dehumidificationOption = False
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            _ = loop.run_until_complete(zone.setHumidityMode("BAD_MODE"))
        except S30Exception as e:
            ex = e
        assert ex is not None
        assert ex.error_code == EC_BAD_PARAMETERS
        assert "BAD_MODE" in ex.message
        assert mock_message_helper.call_count == 0
