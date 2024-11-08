"""Tests temperature and humidity setpoints"""
import json
from unittest.mock import patch

import pytest
from lennoxs30api.s30api_async import lennox_zone, s30api_async, lennox_system
from lennoxs30api.s30exception import EC_BAD_PARAMETERS, S30Exception


@pytest.mark.asyncio
async def test_hsp_f(api: s30api_async):
    """Test setting heat setpoint f"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.single_setpoint_mode is False
    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await zone.perform_setpoint(r_hsp=71)
        mock_message_helper.assert_called_once()
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        t_schedule = jsbody["Data"]["schedules"][0]
        assert t_schedule["id"] == zone.getManualModeScheduleId()
        t_period = t_schedule["schedule"]["periods"][0]["period"]
        assert t_period["hsp"] == 71
        assert t_period["hspC"] == 21.5
        schedule = lsystem.getSchedule(zone.getManualModeScheduleId())
        zperiod = schedule.getPeriod(0)

        assert t_period["csp"] == zperiod.csp
        assert t_period["cspC"] == zperiod.cspC


@pytest.mark.asyncio
async def test_hsp_c(api: s30api_async):
    """Test setting heat setpoint c"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.single_setpoint_mode is False
    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await zone.perform_setpoint(r_hspC=21.5)
        mock_message_helper.assert_called_once()
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        t_schedule = jsbody["Data"]["schedules"][0]
        assert t_schedule["id"] == zone.getManualModeScheduleId()
        t_period = t_schedule["schedule"]["periods"][0]["period"]
        assert t_period["hsp"] == 71
        assert t_period["hspC"] == 21.5
        schedule = lsystem.getSchedule(zone.getManualModeScheduleId())
        zperiod = schedule.getPeriod(0)

        assert t_period["csp"] == zperiod.csp
        assert t_period["cspC"] == zperiod.cspC


@pytest.mark.asyncio
async def test_csp_f(api: s30api_async):
    """Test cool setpoint c"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.single_setpoint_mode is False
    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await zone.perform_setpoint(r_csp=73)
        mock_message_helper.assert_called_once()
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        t_schedule = jsbody["Data"]["schedules"][0]
        assert t_schedule["id"] == zone.getManualModeScheduleId()
        t_period = t_schedule["schedule"]["periods"][0]["period"]
        assert t_period["csp"] == 73
        assert t_period["cspC"] == 23
        schedule = lsystem.getSchedule(zone.getManualModeScheduleId())
        zperiod = schedule.getPeriod(0)

        assert t_period["hsp"] == zperiod.hsp
        assert t_period["hspC"] == zperiod.hspC


@pytest.mark.asyncio
async def test_csp_c(api: s30api_async):
    """Test cool setpoint c"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.single_setpoint_mode is False
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await zone.perform_setpoint(r_cspC=23)
        mock_message_helper.assert_called_once()
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        t_schedule = jsbody["Data"]["schedules"][0]
        assert t_schedule["id"] == zone.getManualModeScheduleId()
        t_period = t_schedule["schedule"]["periods"][0]["period"]
        assert t_period["csp"] == 73
        assert t_period["cspC"] == 23
        schedule = lsystem.getSchedule(zone.getManualModeScheduleId())
        zperiod = schedule.getPeriod(0)

        assert t_period["hsp"] == zperiod.hsp
        assert t_period["hspC"] == zperiod.hspC


@pytest.mark.asyncio
async def test_hcsp_f(api: s30api_async):
    """Test heat and cool setpoints f"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.single_setpoint_mode is False

    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await zone.perform_setpoint(r_hsp=64, r_csp=78)
        mock_message_helper.assert_called_once()
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        t_schedule = jsbody["Data"]["schedules"][0]
        assert t_schedule["id"] == zone.getManualModeScheduleId()
        t_period = t_schedule["schedule"]["periods"][0]["period"]
        assert t_period["csp"] == 78
        assert t_period["cspC"] == 25.5
        assert t_period["hsp"] == 64
        assert t_period["hspC"] == 18
        assert len(t_period) == 4


@pytest.mark.asyncio
async def test_hcsp_c(api: s30api_async):
    """Test heat and cool setpoints c"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.single_setpoint_mode is False

    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await zone.perform_setpoint(r_hspC=18, r_cspC=25.5)
        mock_message_helper.assert_called_once()
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        t_schedule = jsbody["Data"]["schedules"][0]
        assert t_schedule["id"] == zone.getManualModeScheduleId()
        t_period = t_schedule["schedule"]["periods"][0]["period"]
        assert t_period["csp"] == 78
        assert t_period["cspC"] == 25.5
        assert t_period["hsp"] == 64
        assert t_period["hspC"] == 18
        assert len(t_period) == 4


@pytest.mark.asyncio
async def test_sp_f(api_single_setpoint: s30api_async):
    """Test single setpoint f"""
    api = api_single_setpoint
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.single_setpoint_mode is True
    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await zone.perform_setpoint(r_sp=78)
        mock_message_helper.assert_called_once()
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        t_schedule = jsbody["Data"]["schedules"][0]
        assert t_schedule["id"] == zone.getManualModeScheduleId()
        t_period = t_schedule["schedule"]["periods"][0]["period"]
        assert t_period["sp"] == 78
        assert t_period["spC"] == 25.5
        assert len(t_period) == 2


@pytest.mark.asyncio
async def test_sp_c(api_single_setpoint: s30api_async):
    """Test single setpoint c"""
    api = api_single_setpoint
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.single_setpoint_mode is True
    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await zone.perform_setpoint(r_spC=25.5)
        mock_message_helper.assert_called_once()
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        t_schedule = jsbody["Data"]["schedules"][0]
        assert t_schedule["id"] == zone.getManualModeScheduleId()
        t_period = t_schedule["schedule"]["periods"][0]["period"]
        assert t_period["sp"] == 78
        assert t_period["spC"] == 25.5
        assert len(t_period) == 2


@pytest.mark.asyncio
async def test_override(api: s30api_async):
    """Test schedule override"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.single_setpoint_mode is False
    zone: lennox_zone = lsystem.getZone(0)
    # In the default config all zones are in manual mode, here we fake it to follow the
    # "summer" scheduled such that an override schedule will need to be created.
    zone.scheduleId = 1
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await zone.perform_setpoint(r_hsp=71)
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
        assert t_period["hsp"] == 71
        assert t_period["hspC"] == 21.5
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

    # Test a setpoint when the zone is already override
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        # Fake the zone to think it is in override mode.
        zone.scheduleId = zone.getOverrideScheduleId()
        await zone.perform_setpoint(r_csp=75)
        assert mock_message_helper.call_count == 1

        m1 = mock_message_helper.call_args_list[0]
        sys_id = m1.args[0]
        message = m1.args[1]
        assert sys_id == lsystem.sysId
        jsbody = json.loads("{" + message + "}")
        t_schedule = jsbody["Data"]["schedules"][0]
        assert t_schedule["id"] == zone.getOverrideScheduleId()
        t_period = t_schedule["schedule"]["periods"][0]["period"]
        assert t_period["csp"] == 75
        assert t_period["cspC"] == 24
        assert t_period["hsp"] == zone.hsp
        assert t_period["hspC"] == zone.hspC
        assert len(t_period) == 4


@pytest.mark.asyncio
async def test_setpoint_away_mode(api: s30api_async):
    """Test schedule override"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.single_setpoint_mode is False
    lsystem.manualAwayMode = True
    zone: lennox_zone = lsystem.getZone(0)
    zone.scheduleId = 1
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await zone.perform_setpoint(r_hsp=71)
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
        assert t_period["hsp"] == 71
        assert t_period["hspC"] == 21.5


@pytest.mark.asyncio
async def test_perform_schedule_setpoint_no_values(api: s30api_async):
    """Perform setpoing with no values"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.single_setpoint_mode is False
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await lsystem.perform_schedule_setpoint(0, 16)
        assert exc.value.error_code == EC_BAD_PARAMETERS
        assert mock_message_helper.call_count == 0


@pytest.mark.asyncio
async def test_set_humidify_setpoint(api_single_setpoint: s30api_async):
    """Test humidify setpoint"""
    api = api_single_setpoint
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.single_setpoint_mode is True
    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await zone.perform_humidify_setpoint(r_husp=40)
        mock_message_helper.assert_called_once()
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        t_schedule = jsbody["Data"]["schedules"][0]
        assert t_schedule["id"] == zone.getManualModeScheduleId()
        t_period = t_schedule["schedule"]["periods"][0]["period"]
        assert t_period["husp"] == 40

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await zone.perform_humidify_setpoint(r_husp=400)
        ex: S30Exception = exc.value
        assert ex.error_code == EC_BAD_PARAMETERS
        assert "400" in ex.message
        assert str(zone.maxHumSp) in ex.message
        assert str(zone.minHumSp) in ex.message
        assert mock_message_helper.call_count == 0

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await zone.perform_humidify_setpoint(r_husp=4)
        ex: S30Exception = exc.value
        assert ex.error_code == EC_BAD_PARAMETERS
        assert "4" in ex.message
        assert str(zone.maxHumSp) in ex.message
        assert str(zone.minHumSp) in ex.message
        assert mock_message_helper.call_count == 0


@pytest.mark.asyncio
async def test_set_dehumidify_setpoint(api_single_setpoint: s30api_async):
    """Test setting the dehumidify setpoint"""
    api = api_single_setpoint
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.single_setpoint_mode is True
    zone: lennox_zone = lsystem.getZone(0)
    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        await zone.perform_humidify_setpoint(r_desp=60)
        mock_message_helper.assert_called_once()
        arg0 = mock_message_helper.await_args[0][0]
        assert arg0 == lsystem.sysId
        arg1 = mock_message_helper.await_args[0][1]
        jsbody = json.loads("{" + arg1 + "}")

        t_schedule = jsbody["Data"]["schedules"][0]
        assert t_schedule["id"] == zone.getManualModeScheduleId()
        t_period = t_schedule["schedule"]["periods"][0]["period"]
        assert t_period["desp"] == 60

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await zone.perform_humidify_setpoint(r_desp=400)
        ex: S30Exception = exc.value
        assert ex.error_code == EC_BAD_PARAMETERS
        assert "400" in ex.message
        assert str(zone.maxDehumSp) in ex.message
        assert str(zone.minDehumSp) in ex.message
        assert mock_message_helper.call_count == 0

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await zone.perform_humidify_setpoint(r_desp=4)
        ex: S30Exception = exc.value
        assert ex.error_code == EC_BAD_PARAMETERS
        assert "4" in ex.message
        assert str(zone.maxDehumSp) in ex.message
        assert str(zone.minDehumSp) in ex.message
        assert mock_message_helper.call_count == 0

    with patch.object(api, "publishMessageHelper") as mock_message_helper:
        with pytest.raises(S30Exception) as exc:
            await zone.perform_humidify_setpoint()
        ex: S30Exception = exc.value
        assert ex.error_code == EC_BAD_PARAMETERS
        assert mock_message_helper.call_count == 0
