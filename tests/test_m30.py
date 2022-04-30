import json
import os
import asyncio
import pytest

from unittest.mock import patch

from lennoxs30api.s30exception import S30Exception
from lennoxs30api.s30api_async import (
    LENNOX_HVAC_HEAT,
    LENNOX_SA_SETPOINT_STATE_HOME,
    LENNOX_SA_STATE_DISABLED,
    lennox_zone,
    s30api_async,
    lennox_system,
)
from lennoxs30api.lennox_home import lennox_home


def loadfile(name) -> json:
    script_dir = os.path.dirname(__file__) + "/messages/"
    file_path = os.path.join(script_dir, name)
    with open(file_path) as f:
        data = json.load(f)
    return data


@pytest.fixture
def api_m30(single_setpoint: bool = False) -> s30api_async:
    asyncio.set_event_loop(asyncio.new_event_loop())

    api = s30api_async("myemail@email.com", "mypassword", None)
    data = loadfile("login_response.json")
    api.process_login_response(data)

    data = loadfile("m30_config_response.json")
    api.processMessage(data)

    data = loadfile("m30_device_response.json")
    api.processMessage(data)

    return api


def test_process_setpoint(api_m30):
    api = api_m30
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


def test_process_configuration_message(api_m30):
    api = api_m30
    lsystem: lennox_system = api.getSystems()[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.productType == "M30"
    assert lsystem.name == "Downstairs"
    assert lsystem.numberOfZones == 1
    assert lsystem.outdoorTemperature == 77
    assert lsystem.outdoorTemperatureC == 25
    assert lsystem.temperatureUnit == "F"

    assert lsystem.serialNumber == "A220K00436"
    assert lsystem.unique_id() == lsystem.sysId
    assert lsystem.softwareVersion == "03.00.0384"

    assert lsystem.indoorUnitType == "none"
    assert lsystem.has_indoor_unit == False

    assert lsystem.outdoorUnitType == "air conditioner"
    assert lsystem.has_emergency_heat() == False
    assert lsystem.has_outdoor_unit == True

    assert lsystem.diagPoweredHours == 8849
    assert lsystem.diagRuntime == 1288
    assert lsystem.diagVentilationRuntime == 0
    assert lsystem.humidifierType == "none"
    assert lsystem.ventilationUnitType == "none"
    assert lsystem.supports_ventilation() == False
    assert lsystem.ventilationControlMode == "ashrae"
    assert lsystem.feelsLikeMode == True
    assert lsystem.ventilatingUntilTime == ""

    # Away Mode and Smart Away Tests
    assert lsystem.manualAwayMode == False == lsystem.get_manual_away_mode()
    assert lsystem.sa_enabled == False
    assert lsystem.sa_reset == False
    assert lsystem.sa_cancel == False
    assert lsystem.sa_state == LENNOX_SA_STATE_DISABLED
    assert lsystem.sa_setpointState == LENNOX_SA_SETPOINT_STATE_HOME
    assert lsystem.get_smart_away_mode() == False
    assert lsystem.get_away_mode() == False

    zones = lsystem.getZoneList()
    assert len(zones) == 4

    zone_1: lennox_zone = zones[0]

    assert zone_1.name == "Zone 1"
    assert zone_1.id == 0
    assert zone_1.coolingOption == True
    assert zone_1.csp == 77 == zone_1.getCoolSP()
    assert zone_1.dehumidificationOption == False
    assert zone_1.desp == 50
    assert zone_1.emergencyHeatingOption == False
    assert zone_1.fanMode == "auto" == zone_1.getFanMode()
    assert zone_1.heatingOption == True
    assert zone_1.hsp == 73 == zone_1.getHeatSP()
    assert zone_1.hspC == 23
    assert zone_1.humOperation == "off"
    assert zone_1.humidificationOption == False
    assert zone_1.humidity == 27 == zone_1.getHumidity()
    assert zone_1.humidityMode == "off"
    assert zone_1.husp == 40 == zone_1.getHumidifySetpoint()
    assert zone_1.maxCsp == 99
    assert zone_1.maxCspC == 37
    assert zone_1.minCsp == 60
    assert zone_1.minCspC == 16
    assert zone_1.maxHsp == 90
    assert zone_1.maxHspC == 32
    assert zone_1.minHsp == 40
    assert zone_1.minHspC == 4.5
    assert zone_1.sp == 73
    assert zone_1.spC == 23

    assert zone_1.maxDehumSp == 60
    assert zone_1.scheduleId == 16 == zone_1.getManualModeScheduleId()
    assert zone_1.systemMode == LENNOX_HVAC_HEAT == zone_1.getSystemMode()
    assert zone_1.tempOperation == "heating"
    assert zone_1.temperature == 73 == zone_1.getTemperature()
    assert zone_1.temperatureC == 23 == zone_1.getTemperatureC()
    assert zone_1.heatCoast == False
    assert zone_1.defrost == False
    assert zone_1.balancePoint == "none"
    assert zone_1.aux == False
    assert zone_1.coolCoast == False
    assert zone_1.ssr == False

    assert zone_1._system.sysId == "0000000-0000-0000-0000-000000000001"

    assert zone_1.getTargetTemperatureF() == zone_1.hsp
    assert zone_1.getTargetTemperatureC() == zone_1.hspC

    zone_2: lennox_zone = zones[1]

    assert zone_2.name == "Zone 2"
    assert zone_2.id == 1
    assert zone_2.is_zone_active() == False

    zone_3: lennox_zone = zones[2]

    assert zone_3.name == "Zone 3"
    assert zone_3.id == 2
    assert zone_3.is_zone_active() == False

    zone_4: lennox_zone = zones[3]
    assert zone_4.name == "Zone 4"
    assert zone_4.id == 3
    assert zone_4.is_zone_active() == False
