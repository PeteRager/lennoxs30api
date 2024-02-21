"""Test setting the hvac system mode"""

import json
from unittest.mock import patch

import pytest
from lennoxs30api import s30api_async

from lennoxs30api.s30api_async import (
    LENNOX_HVAC_COOL,
    LENNOX_HVAC_EMERGENCY_HEAT,
    LENNOX_HVAC_HEAT,
    LENNOX_HVAC_HEAT_COOL,
    LENNOX_HVAC_OFF,
    lennox_zone,
    lennox_system,
)
from lennoxs30api.s30exception import S30Exception


@pytest.mark.asyncio
async def test_set_system_mode_emergency_heat(api: s30api_async):
    """Tests setting mode to emergency heat"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    # This system does not have emergency heat, therefore we should be able to set it
    assert lsystem.has_emergency_heat() is False
    zone: lennox_zone = lsystem.getZone(0)
    assert zone.emergencyHeatingOption is False
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as e:
            await zone.setHVACMode(LENNOX_HVAC_EMERGENCY_HEAT)
        assert mock_message_helper.call_count == 0
        ex: S30Exception = e.value
        assert "emergency heat" in ex.message

    # This system has emergency heat
    assert lsystem.has_emergency_heat() is False
    zone: lennox_zone = lsystem.getZone(0)
    zone.emergencyHeatingOption = True
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await zone.setHVACMode(LENNOX_HVAC_EMERGENCY_HEAT)
        assert mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        t_schedule = jsbody["Data"]["schedules"][0]
        assert t_schedule["id"] == zone.getManualModeScheduleId()
        t_period = t_schedule["schedule"]["periods"][0]["period"]
        assert t_period["systemMode"] == LENNOX_HVAC_EMERGENCY_HEAT
        assert len(t_period) == 1

    lsystem: lennox_system = api.system_list[2]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000003"
    # This system has emergency heat
    assert lsystem.has_emergency_heat() is True
    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await zone.setHVACMode(LENNOX_HVAC_EMERGENCY_HEAT)
        assert mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        t_schedule = jsbody["Data"]["schedules"][0]
        assert t_schedule["id"] == zone.getManualModeScheduleId()
        t_period = t_schedule["schedule"]["periods"][0]["period"]
        assert t_period["systemMode"] == LENNOX_HVAC_EMERGENCY_HEAT
        assert len(t_period) == 1


@pytest.mark.asyncio
async def test_set_hvac_mode_cool(api: s30api_async):
    """Tests setting mode to cool"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    zone: lennox_zone = lsystem.getZone(0)
    zone.coolingOption = False
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as e:
            await zone.setHVACMode(LENNOX_HVAC_COOL)
        assert mock_message_helper.call_count == 0
        ex: S30Exception = e.value
        assert LENNOX_HVAC_COOL in ex.message

    zone.coolingOption = True
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await zone.setHVACMode(LENNOX_HVAC_COOL)
        assert mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        t_schedule = jsbody["Data"]["schedules"][0]
        assert t_schedule["id"] == zone.getManualModeScheduleId()
        t_period = t_schedule["schedule"]["periods"][0]["period"]

        assert t_period["systemMode"] == LENNOX_HVAC_COOL
        assert len(t_period) == 1


@pytest.mark.asyncio
async def test_set_hvac_mode_heat_cool_not_manual(api: s30api_async):
    """Tests setting mode to heat cool"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    zone: lennox_zone = lsystem.getZone(0)
    zone.scheduleId = 22
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await zone.setHVACMode(LENNOX_HVAC_COOL)
        assert mock_message_helper.call_count == 2
        m1 = mock_message_helper.call_args_list[0]
        arg0 = m1[0][0]
        assert arg0 == lsystem.sysId
        arg1 = m1[0][1]
        jsbody = json.loads("{" + arg1 + "}")
        t_schedule = jsbody["Data"]["zones"][0]["config"]
        assert t_schedule["scheduleId"] == zone.getManualModeScheduleId()

        m1 = mock_message_helper.call_args_list[1]
        arg0 = m1[0][0]
        assert arg0 == lsystem.sysId
        arg1 = m1[0][1]
        jsbody = json.loads("{" + arg1 + "}")
        t_schedule = jsbody["Data"]["schedules"][0]
        assert t_schedule["id"] == zone.getManualModeScheduleId()
        t_period = t_schedule["schedule"]["periods"][0]["period"]
        assert t_period["systemMode"] == LENNOX_HVAC_COOL
        assert len(t_period) == 1


@pytest.mark.asyncio
async def test_set_hvac_mode_heat(api: s30api_async):
    """Tests setting mode to heat"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    zone: lennox_zone = lsystem.getZone(0)
    zone.heatingOption = False
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as e:
            await zone.setHVACMode(LENNOX_HVAC_HEAT)
        assert mock_message_helper.call_count == 0
        ex: S30Exception = e.value
        assert LENNOX_HVAC_HEAT in ex.message

    zone.heatingOption = True
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await zone.setHVACMode(LENNOX_HVAC_HEAT)
        assert mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        t_schedule = jsbody["Data"]["schedules"][0]
        assert t_schedule["id"] == zone.getManualModeScheduleId()
        t_period = t_schedule["schedule"]["periods"][0]["period"]

        assert t_period["systemMode"] == LENNOX_HVAC_HEAT
        assert len(t_period) == 1


@pytest.mark.asyncio
async def test_set_hvac_mode_heat_cool(api: s30api_async):
    """Tests setting mode to heat cool"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    zone: lennox_zone = lsystem.getZone(0)
    zone.heatingOption = False
    zone.coolingOption = True
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as e:
            await zone.setHVACMode(LENNOX_HVAC_HEAT_COOL)
        assert mock_message_helper.call_count == 0
        ex: S30Exception = e.value
        assert LENNOX_HVAC_HEAT_COOL in ex.message

    zone.heatingOption = True
    zone.coolingOption = False
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as e:
            await zone.setHVACMode(LENNOX_HVAC_HEAT_COOL)
        assert mock_message_helper.call_count == 0
        ex: S30Exception = e.value
        assert LENNOX_HVAC_HEAT_COOL in ex.message

    zone.heatingOption = True
    zone.coolingOption = True
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await zone.setHVACMode(LENNOX_HVAC_HEAT_COOL)
        assert mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        t_schedule = jsbody["Data"]["schedules"][0]
        assert t_schedule["id"] == zone.getManualModeScheduleId()
        t_period = t_schedule["schedule"]["periods"][0]["period"]

        assert t_period["systemMode"] == LENNOX_HVAC_HEAT_COOL
        assert len(t_period) == 1


@pytest.mark.asyncio
async def test_set_hvac_mode_off(api: s30api_async):
    """Tests setting mode to off"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    zone: lennox_zone = lsystem.getZone(0)

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await zone.setHVACMode(LENNOX_HVAC_OFF)
        assert mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        t_schedule = jsbody["Data"]["schedules"][0]
        assert t_schedule["id"] == zone.getManualModeScheduleId()
        t_period = t_schedule["schedule"]["periods"][0]["period"]

        assert t_period["systemMode"] == LENNOX_HVAC_OFF
        assert len(t_period) == 1


@pytest.mark.asyncio
async def test_set_hvac_mode_bad_mode(api: s30api_async):
    """Tests setting mode to an invalid name"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    zone: lennox_zone = lsystem.getZone(0)
    zone.heatingOption = False
    zone.coolingOption = True
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as e:
            await zone.setHVACMode("BOGUS MODE")
        assert mock_message_helper.call_count == 0
        ex: S30Exception = e.value
        assert "BOGUS MODE" in ex.message
