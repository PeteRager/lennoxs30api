"""Test setting the fan mode"""
import json
from unittest.mock import patch

import pytest
from lennoxs30api.s30api_async import lennox_zone, s30api_async, lennox_system
from lennoxs30api.s30exception import EC_BAD_PARAMETERS, S30Exception


@pytest.mark.asyncio
async def test_set_fan_mode(api: s30api_async):
    """Test setting fan mode"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await zone.setFanMode("circulate")
        mock_message_helper.assert_called_once()
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        t_schedule = jsbody["Data"]["schedules"][0]
        assert t_schedule["id"] == zone.getManualModeScheduleId()
        t_period = t_schedule["schedule"]["periods"][0]["period"]
        assert t_period["fanMode"] == "circulate"

@pytest.mark.asyncio
async def test_set_fan_mode_away_mode(api: s30api_async):
    """Test setting the fan when in away mode"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    lsystem.manualAwayMode = True
    zone: lennox_zone = lsystem.getZone(0)
    zone.scheduleId = 1
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await zone.setFanMode("circulate")
        assert mock_message_helper.call_count == 1

        # First message should be the configuration of the schedule override
        m1 = mock_message_helper.call_args_list[0]
        sys_id = m1.args[0]
        message = m1.args[1]
        assert sys_id == lsystem.sysId
        jsbody = json.loads("{" + message + "}")

        t_schedule = jsbody["Data"]["schedules"][0]
        assert t_schedule["id"] == zone.getAwayModeScheduleId()
        t_period = t_schedule["schedule"]["periods"][0]["period"]
        assert t_period["fanMode"] == "circulate"

@pytest.mark.asyncio
async def test_set_fan_mode_override(api: s30api_async):
    """Test schedule override"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.single_setpoint_mode is False
    zone: lennox_zone = lsystem.getZone(0)
    # In the default config all zones are in manual mode, here we fake it to follow the
    # "summer" scheduled such that an override schedule will need to be created.
    zone.scheduleId = 1
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await zone.setFanMode("circulate")
        assert mock_message_helper.call_count == 3

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
        assert t_period["humidityMode"] == zone.humidityMode
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

        # Third message should set the fan mode
        m1 = mock_message_helper.call_args_list[2]
        sys_id = m1.args[0]
        message = m1.args[1]
        assert sys_id == lsystem.sysId
        jsbody = json.loads("{" + message + "}")
        t_schedule = jsbody["Data"]["schedules"][0]
        assert t_schedule["id"] == zone.getOverrideScheduleId()
        t_period = t_schedule["schedule"]["periods"][0]["period"]
        assert t_period["fanMode"] == "circulate"

    # Test setting fan when one is alread in override
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        # Fake the zone to think it is in override mode.
        zone.scheduleId = zone.getOverrideScheduleId()
        await zone.setFanMode("circulate")
        assert mock_message_helper.call_count == 1

        m1 = mock_message_helper.call_args_list[0]
        sys_id = m1.args[0]
        message = m1.args[1]
        assert sys_id == lsystem.sysId
        jsbody = json.loads("{" + message + "}")
        t_schedule = jsbody["Data"]["schedules"][0]
        assert t_schedule["id"] == zone.getOverrideScheduleId()
        t_period = t_schedule["schedule"]["periods"][0]["period"]
        assert t_period["fanMode"] == "circulate"

@pytest.mark.asyncio
async def test_set_fan_mode_invalid(api: s30api_async):
    """Tests invalid mode"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.single_setpoint_mode is False
    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await zone.setFanMode("BadMode")
        assert mock_message_helper.call_count == 0
        ex: S30Exception = exc.value
        assert "BadMode" in ex.message
