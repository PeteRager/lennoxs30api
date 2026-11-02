"""Tests editing schedule periods"""

import json
from unittest.mock import patch

import pytest
from lennoxs30api.s30api_async import lennox_system, s30api_async
from lennoxs30api.s30exception import EC_BAD_PARAMETERS, S30Exception


def published_data(mock_message_helper, lsystem: lennox_system) -> dict:
    """Returns the Data element of the published message"""
    mock_message_helper.assert_called_once()
    arg0 = mock_message_helper.await_args[0][0]
    assert arg0 == lsystem.sysId
    arg1 = mock_message_helper.await_args[0][1]
    jsbody = json.loads("{" + arg1 + "}")
    return jsbody["Data"]


@pytest.mark.asyncio
async def test_set_schedule_period_start_time(api: s30api_async):
    """Test setting only the start time of a period"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        # 106200 is day 1 at 05:30
        await lsystem.set_schedule_period(1, 4, startTime=106200)
        data = published_data(mock_message_helper, lsystem)

        t_schedule = data["schedules"][0]
        assert t_schedule["id"] == 1
        t_periods = t_schedule["schedule"]["periods"][0]
        assert t_periods["id"] == 4
        # enabled was not requested, so it must not be in the message
        assert "enabled" not in t_periods
        assert t_periods["period"] == {"startTime": 106200}


@pytest.mark.asyncio
async def test_set_schedule_period_message_format(api: s30api_async):
    """Test the published message matches the format the LCC accepts"""
    lsystem: lennox_system = api.system_list[0]
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await lsystem.set_schedule_period(1, 4, startTime=106200, enabled=True, hsp=64, csp=76, fanMode="auto")
        arg1 = mock_message_helper.await_args[0][1]
        assert arg1 == (
            '"Data":{"schedules": [{"schedule": {"periods": [{"id": 4, "enabled": true, '
            '"period": {"startTime": 106200, "hsp": 64, "hspC": 18.0, "csp": 76, "cspC": 24.5, "fanMode": "auto"}}]}, "id": 1}]}'
        )


@pytest.mark.asyncio
async def test_set_schedule_period_enabled(api: s30api_async):
    """Test disabling a period - this is how the thermostat deletes one"""
    lsystem: lennox_system = api.system_list[0]
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await lsystem.set_schedule_period(1, 5, enabled=False)
        data = published_data(mock_message_helper, lsystem)

        t_periods = data["schedules"][0]["schedule"]["periods"][0]
        assert t_periods["id"] == 5
        assert t_periods["enabled"] is False
        assert t_periods["period"] == {}


@pytest.mark.asyncio
async def test_set_schedule_period_hsp_f(api: s30api_async):
    """Test setting the heat setpoint in faren, the cool setpoint comes from the period"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.single_setpoint_mode is False
    period = lsystem.getSchedule(1).getPeriod(4)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await lsystem.set_schedule_period(1, 4, hsp=64)
        data = published_data(mock_message_helper, lsystem)

        t_period = data["schedules"][0]["schedule"]["periods"][0]["period"]
        assert t_period["hsp"] == 64
        assert t_period["hspC"] == 18.0
        assert t_period["csp"] == period.csp
        assert t_period["cspC"] == period.cspC
        assert "startTime" not in t_period


@pytest.mark.asyncio
async def test_set_schedule_period_hsp_c(api: s30api_async):
    """Test setting the heat setpoint in celsius"""
    lsystem: lennox_system = api.system_list[0]
    period = lsystem.getSchedule(1).getPeriod(4)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await lsystem.set_schedule_period(1, 4, hspC=18.0)
        data = published_data(mock_message_helper, lsystem)

        t_period = data["schedules"][0]["schedule"]["periods"][0]["period"]
        assert t_period["hsp"] == 64
        assert t_period["hspC"] == 18.0
        assert t_period["csp"] == period.csp
        assert t_period["cspC"] == period.cspC


@pytest.mark.asyncio
async def test_set_schedule_period_csp_f(api: s30api_async):
    """Test setting the cool setpoint in faren, the heat setpoint comes from the period"""
    lsystem: lennox_system = api.system_list[0]
    period = lsystem.getSchedule(1).getPeriod(4)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await lsystem.set_schedule_period(1, 4, csp=76)
        data = published_data(mock_message_helper, lsystem)

        t_period = data["schedules"][0]["schedule"]["periods"][0]["period"]
        assert t_period["hsp"] == period.hsp
        assert t_period["hspC"] == period.hspC
        assert t_period["csp"] == 76
        assert t_period["cspC"] == 24.5


@pytest.mark.asyncio
async def test_set_schedule_period_both_setpoints(api: s30api_async):
    """Test setting both setpoints, the specified unit is not converted back"""
    lsystem: lennox_system = api.system_list[0]
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        # The LCC stores the units independently, 64F appears with both 17.5C and 18.0C on a
        # real system, so a specified celsius value must be sent exactly as given.
        await lsystem.set_schedule_period(1, 4, hsp=64, hspC=17.5, csp=76, cspC=24.5)
        data = published_data(mock_message_helper, lsystem)

        t_period = data["schedules"][0]["schedule"]["periods"][0]["period"]
        assert t_period["hsp"] == 64
        assert t_period["hspC"] == 17.5
        assert t_period["csp"] == 76
        assert t_period["cspC"] == 24.5


@pytest.mark.asyncio
async def test_set_schedule_period_single_setpoint(api_single_setpoint: s30api_async):
    """Test the single setpoint mode sends sp and spC"""
    api = api_single_setpoint
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.single_setpoint_mode is True
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await lsystem.set_schedule_period(1, 4, sp=72)
        data = published_data(mock_message_helper, lsystem)

        t_period = data["schedules"][0]["schedule"]["periods"][0]["period"]
        assert t_period["sp"] == 72
        assert t_period["spC"] == 22.0
        assert "hsp" not in t_period
        assert "csp" not in t_period


@pytest.mark.asyncio
async def test_set_schedule_period_single_setpoint_c(api_single_setpoint: s30api_async):
    """Test the single setpoint mode in celsius"""
    api = api_single_setpoint
    lsystem: lennox_system = api.system_list[0]
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await lsystem.set_schedule_period(1, 4, spC=22.0)
        data = published_data(mock_message_helper, lsystem)

        t_period = data["schedules"][0]["schedule"]["periods"][0]["period"]
        assert t_period["sp"] == 72
        assert t_period["spC"] == 22.0


@pytest.mark.asyncio
async def test_set_schedule_period_modes(api: s30api_async):
    """Test setting the modes and the humidity setpoints"""
    lsystem: lennox_system = api.system_list[0]
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await lsystem.set_schedule_period(
            1,
            4,
            fanMode="circulate",
            systemMode="heat",
            humidityMode="humidify",
            husp=45,
            desp=55,
        )
        data = published_data(mock_message_helper, lsystem)

        t_period = data["schedules"][0]["schedule"]["periods"][0]["period"]
        assert t_period == {
            "systemMode": "heat",
            "humidityMode": "humidify",
            "husp": 45,
            "desp": 55,
            "fanMode": "circulate",
        }


@pytest.mark.asyncio
async def test_set_schedule_period_week_start_times(api: s30api_async):
    """Test the start times of the shipped schedule match day * 86400 plus the time of day"""
    lsystem: lennox_system = api.system_list[0]
    schedule = lsystem.getSchedule(1)
    assert schedule.name == "summer"
    assert schedule.periodCount == 28
    for period_id in range(28):
        period = schedule.getPeriod(period_id)
        day = period_id // 4
        assert period.startTime // 86400 == day
    # day 1 period 0 is 06:00, day 6 period 3 is 21:00
    assert schedule.getPeriod(4).startTime == 86400 + 6 * 3600
    assert schedule.getPeriod(27).startTime == 6 * 86400 + 21 * 3600


@pytest.mark.asyncio
async def test_set_schedule_period_empty_slot(api: s30api_async):
    """Test schedule slots 5 - 15 are rejected rather than guessed at"""
    lsystem: lennox_system = api.system_list[0]
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await lsystem.set_schedule_period(7, 0, startTime=3600)
        ex: S30Exception = exc.value
        assert ex.error_code == EC_BAD_PARAMETERS
        assert ex.reference == 1
        assert "7" in ex.message
        assert "empty slot" in ex.message
        assert mock_message_helper.call_count == 0


@pytest.mark.asyncio
async def test_set_schedule_period_unknown_schedule(api: s30api_async):
    """Test an unknown schedule id"""
    lsystem: lennox_system = api.system_list[0]
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await lsystem.set_schedule_period(99, 0, startTime=3600)
        ex: S30Exception = exc.value
        assert ex.error_code == EC_BAD_PARAMETERS
        assert ex.reference == 2
        assert "99" in ex.message
        assert mock_message_helper.call_count == 0


@pytest.mark.asyncio
async def test_set_schedule_period_unknown_period(api: s30api_async):
    """Test a period id that is not in the schedule"""
    lsystem: lennox_system = api.system_list[0]
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await lsystem.set_schedule_period(1, 28, startTime=3600)
        ex: S30Exception = exc.value
        assert ex.error_code == EC_BAD_PARAMETERS
        assert ex.reference == 3
        assert "28" in ex.message
        assert mock_message_helper.call_count == 0

    # the manual mode schedules only have a single period
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await lsystem.set_schedule_period(16, 1, startTime=3600)
        assert exc.value.reference == 3
        assert mock_message_helper.call_count == 0


@pytest.mark.asyncio
async def test_set_schedule_period_no_values(api: s30api_async):
    """Test calling with nothing to set"""
    lsystem: lennox_system = api.system_list[0]
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await lsystem.set_schedule_period(1, 4)
        ex: S30Exception = exc.value
        assert ex.error_code == EC_BAD_PARAMETERS
        assert ex.reference == 4
        assert mock_message_helper.call_count == 0


@pytest.mark.asyncio
async def test_set_schedule_period_bad_modes(api: s30api_async):
    """Test the mode validation"""
    lsystem: lennox_system = api.system_list[0]
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await lsystem.set_schedule_period(1, 4, fanMode="bogus")
        assert exc.value.error_code == EC_BAD_PARAMETERS
        assert exc.value.reference == 5

        with pytest.raises(S30Exception) as exc:
            await lsystem.set_schedule_period(1, 4, systemMode="bogus")
        assert exc.value.reference == 6

        with pytest.raises(S30Exception) as exc:
            await lsystem.set_schedule_period(1, 4, humidityMode="bogus")
        assert exc.value.reference == 7
        assert mock_message_helper.call_count == 0


@pytest.mark.asyncio
async def test_set_schedule_period_bad_start_time(api: s30api_async):
    """Test the start time must be within the week"""
    lsystem: lennox_system = api.system_list[0]
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await lsystem.set_schedule_period(1, 4, startTime=604800)
        assert exc.value.error_code == EC_BAD_PARAMETERS
        assert exc.value.reference == 8

        with pytest.raises(S30Exception) as exc:
            await lsystem.set_schedule_period(1, 4, startTime=-1)
        assert exc.value.reference == 8
        assert mock_message_helper.call_count == 0

    # the last second of the week is valid
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await lsystem.set_schedule_period(1, 4, startTime=604799)
        assert mock_message_helper.call_count == 1


@pytest.mark.asyncio
async def test_set_schedule_period_wrong_setpoint_mode(api: s30api_async, api_single_setpoint: s30api_async):
    """Test sp and spC are rejected on a split setpoint system and vice versa"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.single_setpoint_mode is False
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await lsystem.set_schedule_period(1, 4, sp=72)
        assert exc.value.error_code == EC_BAD_PARAMETERS
        assert exc.value.reference == 9
        assert mock_message_helper.call_count == 0

    ssystem: lennox_system = api_single_setpoint.system_list[0]
    assert ssystem.single_setpoint_mode is True
    with patch.object(api_single_setpoint, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await ssystem.set_schedule_period(1, 4, hsp=64)
        assert exc.value.error_code == EC_BAD_PARAMETERS
        assert exc.value.reference == 10
        assert mock_message_helper.call_count == 0


@pytest.mark.asyncio
async def test_set_schedule_period_deadband(api: s30api_async):
    """Test the heat and cool setpoints must be seperated by the deadband"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.changeover_temp_deadband_f == 3
    assert lsystem.changeover_temp_deadband_c == 1.5
    # period 4 has hsp 62 hspC 16.5
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await lsystem.set_schedule_period(1, 4, csp=63)
        assert exc.value.error_code == EC_BAD_PARAMETERS
        assert exc.value.reference == 11
        assert mock_message_helper.call_count == 0

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await lsystem.set_schedule_period(1, 4, csp=65, cspC=17.5)
        assert exc.value.error_code == EC_BAD_PARAMETERS
        assert exc.value.reference == 12
        assert mock_message_helper.call_count == 0


@pytest.mark.asyncio
async def test_set_schedule_name(api: s30api_async):
    """Test renaming a schedule"""
    lsystem: lennox_system = api.system_list[0]
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await lsystem.set_schedule_name(4, "shoulder season")
        data = published_data(mock_message_helper, lsystem)

        t_schedule = data["schedules"][0]
        assert t_schedule["id"] == 4
        # names contain spaces, the message must not have them stripped
        assert t_schedule["schedule"] == {"name": "shoulder season"}


@pytest.mark.asyncio
async def test_set_schedule_name_errors(api: s30api_async):
    """Test the schedule name validation"""
    lsystem: lennox_system = api.system_list[0]
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await lsystem.set_schedule_name(7, "new schedule")
        assert exc.value.error_code == EC_BAD_PARAMETERS
        assert exc.value.reference == 1

        with pytest.raises(S30Exception) as exc:
            await lsystem.set_schedule_name(99, "new schedule")
        assert exc.value.reference == 2

        with pytest.raises(S30Exception) as exc:
            await lsystem.set_schedule_name(4, "")
        assert exc.value.reference == 3
        assert mock_message_helper.call_count == 0


@pytest.mark.asyncio
async def test_schedule_periods_accessor(api: s30api_async):
    """Test the periods accessor returns them in id order"""
    lsystem: lennox_system = api.system_list[0]
    schedule = lsystem.getSchedule(1)
    periods = schedule.periods
    assert len(periods) == 28
    assert [period.id for period in periods] == list(range(28))
    assert periods[4].startTime == 108000
