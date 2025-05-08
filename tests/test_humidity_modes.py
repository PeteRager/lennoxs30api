"""Tests humidty mod"""
import json
from unittest.mock import patch

import pytest
from lennoxs30api import s30api_async
from lennoxs30api.s30api_async import (
    LENNOX_HUMIDITY_MODE_DEHUMIDIFY,
    LENNOX_HUMIDITY_MODE_HUMIDIFY,
    LENNOX_HUMIDITY_MODE_OFF,
    lennox_zone,
    lennox_system,
)

from lennoxs30api.s30exception import EC_BAD_PARAMETERS, S30Exception

@pytest.mark.asyncio
async def test_set_humidity_mode_humidify(api: s30api_async):
    """Test setting the humidity mode"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    zone: lennox_zone = lsystem.getZone(0)
    zone.humidificationOption = False
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await zone.setHumidityMode(LENNOX_HUMIDITY_MODE_HUMIDIFY)
        ex: S30Exception = exc.value
        assert ex.error_code == EC_BAD_PARAMETERS
        assert mock_message_helper.call_count == 0

    zone.humidificationOption = True
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await zone.setHumidityMode(LENNOX_HUMIDITY_MODE_HUMIDIFY)
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


@pytest.mark.asyncio
async def test_set_humidity_mode_dehumidify(api):
    """Test setting dehumidification mode"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    zone: lennox_zone = lsystem.getZone(0)
    zone.dehumidificationOption = False
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await zone.setHumidityMode(LENNOX_HUMIDITY_MODE_DEHUMIDIFY)
        ex: S30Exception = exc.value
        assert ex.error_code == EC_BAD_PARAMETERS
        assert mock_message_helper.call_count == 0

    zone.dehumidificationOption = True
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await zone.setHumidityMode(LENNOX_HUMIDITY_MODE_DEHUMIDIFY)
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


@pytest.mark.asyncio
async def test_set_humidity_mode_off(api):
    """Test setting humidity mode to off"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await zone.setHumidityMode(LENNOX_HUMIDITY_MODE_OFF)
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


@pytest.mark.asyncio
async def test_set_humidity_mode_bad_mode(api):
    """Test error handling when setting a bad mode"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    zone: lennox_zone = lsystem.getZone(0)
    zone.dehumidificationOption = False
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await zone.setHumidityMode("BAD_MODE")
        ex: S30Exception = exc.value
        assert ex.error_code == EC_BAD_PARAMETERS
        assert "BAD_MODE" in ex.message
        assert mock_message_helper.call_count == 0

@pytest.mark.asyncio
async def test_set_humidity_mode_override(api: s30api_async):
    """Test schedule override"""
    lsystem: lennox_system = api.system_list[0]
    zone: lennox_zone = lsystem.getZone(0)
    # In the default config all zones are in manual mode, here we fake it to follow the
    # "summer" scheduled such that an override schedule will need to be created.
    zone.scheduleId = 1
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await zone.setHumidityMode(LENNOX_HUMIDITY_MODE_DEHUMIDIFY)
        assert mock_message_helper.call_count == 2

        # First message should be the configuration of the schedule override
        m1 = mock_message_helper.call_args_list[0]
        sys_id = m1.args[0]
        message = m1.args[1]
        assert sys_id == lsystem.sysId
        jsbody = json.loads("{" + message + "}")

        t_schedule = jsbody["Data"]["schedules"][0]
        assert t_schedule["id"] == zone.getOverrideScheduleId()
        t_period = t_schedule["schedule"]["periods"][0]["period"]
        assert t_period["hsp"] == zone.hsp
        assert t_period["hspC"] == zone.hspC
        assert t_period["desp"] == zone.desp
        assert t_period["cspC"] == zone.cspC
        assert t_period["csp"] == zone.csp
        assert t_period["sp"] == zone.sp
        assert t_period["husp"] == zone.husp
        assert t_period["humidityMode"] == LENNOX_HUMIDITY_MODE_DEHUMIDIFY
        assert t_period["systemMode"] == zone.systemMode
        assert t_period["spC"] == zone.spC
        assert t_period["startTime"] == zone.startTime
        assert t_period["fanMode"] == zone.fanMode

        # Second message should set the zone to follow this schedule
        m2 = mock_message_helper.call_args_list[1]
        sys_id = m2.args[0]
        message = m2.args[1]
        assert sys_id == lsystem.sysId
        jsbody = json.loads("{" + message + "}")

        t_zone = jsbody["Data"]["zones"][0]
        assert t_zone["id"] == zone.id
        hold = t_zone["config"]["scheduleHold"]
        assert hold["scheduleId"] == zone.getOverrideScheduleId()
        assert hold["exceptionType"] == "hold"
        assert hold["enabled"] is True
        assert hold["expiresOn"] == "0"
        assert hold["expirationMode"] == "nextPeriod"
        assert len(hold) == 5

    # Test a setpoint when the zone is already override
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        # Fake the zone to think it is in override mode.
        zone.scheduleId = zone.getOverrideScheduleId()
        await zone.setHumidityMode(LENNOX_HUMIDITY_MODE_DEHUMIDIFY)
        assert mock_message_helper.call_count == 1

        m1 = mock_message_helper.call_args_list[0]
        sys_id = m1.args[0]
        message = m1.args[1]
        assert sys_id == lsystem.sysId
        jsbody = json.loads("{" + message + "}")
        t_schedule = jsbody["Data"]["schedules"][0]
        assert t_schedule["id"] == zone.getOverrideScheduleId()
        t_period = t_schedule["schedule"]["periods"][0]["period"]
        assert t_period["humidityMode"] == LENNOX_HUMIDITY_MODE_DEHUMIDIFY
        assert len(t_period) == 1
