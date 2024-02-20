"""Test setting the hvac system mode"""
import json
from unittest.mock import patch

import pytest
from lennoxs30api import s30api_async

from lennoxs30api.s30api_async import (
    LENNOX_HVAC_EMERGENCY_HEAT,
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
