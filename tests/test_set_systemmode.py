from lennoxs30api.s30api_async import (
    LENNOX_HVAC_EMERGENCY_HEAT,
    lennox_zone,
    lennox_system,
)

import json
import asyncio

from unittest.mock import patch

from lennoxs30api.s30exception import S30Exception


def test_set_systemMode_emergency_heat(api):
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    # This system has emergency heat, therefore we should be able to set it
    assert lsystem.has_emergency_heat() == False
    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        error = False
        try:
            result = loop.run_until_complete(
                zone.setHVACMode(LENNOX_HVAC_EMERGENCY_HEAT)
            )
        except S30Exception as e:
            error = True
        assert error == True
        assert mock_message_helper.call_count == 0

    lsystem: lennox_system = api.system_list[2]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000003"
    # This system does not have emergency heat, therefore we should not be able to set it.
    assert lsystem.has_emergency_heat() == True
    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(zone.setHVACMode(LENNOX_HVAC_EMERGENCY_HEAT))
        assert mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        tSchedule = jsbody["Data"]["schedules"][0]
        assert tSchedule["id"] == zone.getManualModeScheduleId()
        tPeriod = tSchedule["schedule"]["periods"][0]["period"]
        assert tPeriod["systemMode"] == LENNOX_HVAC_EMERGENCY_HEAT
        assert len(tPeriod) == 1
