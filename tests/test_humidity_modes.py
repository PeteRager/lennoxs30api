from lennoxs30api.s30api_async import (
    LENNOX_HUMIDITY_MODE_DEHUMIDIFY,
    LENNOX_HUMIDITY_MODE_HUMIDIFY,
    LENNOX_HUMIDITY_MODE_OFF,
    LENNOX_HVAC_EMERGENCY_HEAT,
    lennox_zone,
    lennox_system,
)

import json
import asyncio

from unittest.mock import patch

from lennoxs30api.s30exception import EC_BAD_PARAMETERS, S30Exception


def test_set_humidity_mode_humidify(api):
    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    zone: lennox_zone = lsystem.getZone(0)
    zone.humidificationOption = False
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(
                zone.setHumidityMode(LENNOX_HUMIDITY_MODE_HUMIDIFY)
            )
        except S30Exception as e:
            ex = e
        assert ex != None
        assert ex.error_code == EC_BAD_PARAMETERS
        assert mock_message_helper.call_count == 0

    zone.humidificationOption = True
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            zone.setHumidityMode(LENNOX_HUMIDITY_MODE_HUMIDIFY)
        )
        assert mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        tSchedule = jsbody["Data"]["schedules"][0]
        assert tSchedule["id"] == zone.getManualModeScheduleId()
        tPeriod = tSchedule["schedule"]["periods"][0]["period"]
        assert tPeriod["humidityMode"] == LENNOX_HUMIDITY_MODE_HUMIDIFY
        assert len(tPeriod) == 1


def test_set_humidity_mode_dehumidify(api):
    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    zone: lennox_zone = lsystem.getZone(0)
    zone.dehumidificationOption = False
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(
                zone.setHumidityMode(LENNOX_HUMIDITY_MODE_DEHUMIDIFY)
            )
        except S30Exception as e:
            ex = e
        assert ex != None
        assert ex.error_code == EC_BAD_PARAMETERS
        assert mock_message_helper.call_count == 0

    zone.dehumidificationOption = True
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            zone.setHumidityMode(LENNOX_HUMIDITY_MODE_DEHUMIDIFY)
        )
        assert mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        tSchedule = jsbody["Data"]["schedules"][0]
        assert tSchedule["id"] == zone.getManualModeScheduleId()
        tPeriod = tSchedule["schedule"]["periods"][0]["period"]
        assert tPeriod["humidityMode"] == LENNOX_HUMIDITY_MODE_DEHUMIDIFY
        assert len(tPeriod) == 1


def test_set_humidity_mode_off(api):
    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(zone.setHumidityMode(LENNOX_HUMIDITY_MODE_OFF))
        assert mock_message_helper.call_count == 1
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        tSchedule = jsbody["Data"]["schedules"][0]
        assert tSchedule["id"] == zone.getManualModeScheduleId()
        tPeriod = tSchedule["schedule"]["periods"][0]["period"]
        assert tPeriod["humidityMode"] == LENNOX_HUMIDITY_MODE_OFF
        assert len(tPeriod) == 1


def test_set_humidity_mode_bad_mode(api):
    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    zone: lennox_zone = lsystem.getZone(0)
    zone.dehumidificationOption = False
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        loop = asyncio.get_event_loop()
        ex = None
        try:
            result = loop.run_until_complete(zone.setHumidityMode("BAD_MODE"))
        except S30Exception as e:
            ex = e
        assert ex != None
        assert ex.error_code == EC_BAD_PARAMETERS
        assert "BAD_MODE" in ex.message
        assert mock_message_helper.call_count == 0
