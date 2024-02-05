"""Test data updates"""
from lennoxs30api.s30api_async import (
    LENNOX_HUMID_OPERATION_HUMID,
    LENNOX_HUMIDITY_MODE_DEHUMIDIFY,
    LENNOX_HUMIDITY_MODE_HUMIDIFY,
    LENNOX_SA_SETPOINT_STATE_HOME,
    LENNOX_SA_STATE_ENABLED_CANCELLED,
    LENNOX_STATUS_GOOD,
    LENNOX_STATUS_NOT_AVAILABLE,
    LENNOX_STATUS_NOT_EXIST,
    lennox_zone,
    s30api_async,
)
from tests.conftest import loadfile


class CallbackHandler(object):
    """Mock for callbacks"""
    def __init__(self):
        self.called = 0

    def update_callback(self):
        """Callback update"""
        self.called = self.called + 1


def test_hvac_mode_change_zone_5(api: s30api_async):
    """Tests hvac mode changing"""
    zone_5: lennox_zone = api.getSystem("0000000-0000-0000-0000-000000000002").getZone(0)
    assert zone_5.getSystemMode() == "off"

    zone_5_callback_all = CallbackHandler()
    zone_5.registerOnUpdateCallback(zone_5_callback_all.update_callback)
    zone_5_callback_system_mode = CallbackHandler()
    zone_5.registerOnUpdateCallback(
        zone_5_callback_system_mode.update_callback, match=["systemMode"]
    )
    zone_5_callback_tempoperation = CallbackHandler()
    zone_5.registerOnUpdateCallback(
        zone_5_callback_tempoperation.update_callback, match=["tempOperation"]
    )

    data = loadfile("mut_sys1_zone1_cool_sched.json")
    api.processMessage(data)
    assert zone_5.getSystemMode() == "cool"
    assert zone_5_callback_all.called == 1
    assert zone_5_callback_system_mode.called == 1
    assert zone_5_callback_tempoperation.called == 0
    # Make sure nothing else changed.
    assert zone_5.name == "Zone 1"
    assert zone_5.id == 0
    assert zone_5.coolingOption is True
    assert zone_5.csp == 78 == zone_5.getCoolSP()
    assert zone_5.cspC == 25.5
    assert zone_5.dehumidificationOption is True
    assert zone_5.desp == 50
    assert zone_5.demand == 0
    assert zone_5.emergencyHeatingOption is False
    assert zone_5.fanMode == "auto" == zone_5.getFanMode()
    assert zone_5.heatingOption is True
    assert zone_5.hsp == 68 == zone_5.getHeatSP()
    assert zone_5.humOperation == "off"
    assert zone_5.humidificationOption is False
    assert zone_5.humidity == 30 == zone_5.getHumidity()
    assert zone_5.humidityStatus == LENNOX_STATUS_GOOD

    assert zone_5.humidityMode == "off"
    assert zone_5.husp == 40 == zone_5.getHumidifySetpoint()
    assert zone_5.maxCsp == 99
    assert zone_5.maxDehumSp == 60
    assert zone_5.maxHsp == 90
    assert zone_5.minHumSp == 15
    assert zone_5.maxHumSp == 45
    assert zone_5.minCsp == 60
    assert zone_5.minHsp == 40
    assert zone_5.scheduleId == 16 == zone_5.getManualModeScheduleId()
    assert zone_5.sp == 73
    assert zone_5.spC == 22.5
    assert zone_5.tempOperation == "off"
    assert zone_5.temperature == 79 == zone_5.getTemperature()
    assert zone_5.temperatureC == 26 == zone_5.getTemperatureC()
    assert zone_5.temperatureStatus == LENNOX_STATUS_GOOD

    assert zone_5.system.sysId == "0000000-0000-0000-0000-000000000002"

    # This file does not change anything.  Sometimes this message is not received.
    data = loadfile("mut_sys1_zone1_status.json")
    api.processMessage(data)

    assert zone_5_callback_all.called == 1
    assert zone_5_callback_system_mode.called == 1
    assert zone_5_callback_tempoperation.called == 0

    # Make sure nothing else changed.
    assert zone_5.name == "Zone 1"
    assert zone_5.id == 0
    assert zone_5.coolingOption is True
    assert zone_5.csp == 78 == zone_5.getCoolSP()
    assert zone_5.dehumidificationOption is True
    assert zone_5.demand == 0
    assert zone_5.desp == 50
    assert zone_5.emergencyHeatingOption is False
    assert zone_5.fanMode == "auto" == zone_5.getFanMode()
    assert zone_5.heatingOption is True
    assert zone_5.hsp == 68 == zone_5.getHeatSP()
    assert zone_5.humOperation == "off"
    assert zone_5.humidificationOption is False
    assert zone_5.humidity == 30 == zone_5.getHumidity()
    assert zone_5.humidityStatus == LENNOX_STATUS_GOOD

    assert zone_5.humidityMode == "off"
    assert zone_5.husp == 40 == zone_5.getHumidifySetpoint()
    assert zone_5.maxCsp == 99
    assert zone_5.maxDehumSp == 60
    assert zone_5.maxHsp == 90
    assert zone_5.minHumSp == 15
    assert zone_5.maxHumSp == 45
    assert zone_5.minCsp == 60
    assert zone_5.minHsp == 40
    assert zone_5.scheduleId == 16 == zone_5.getManualModeScheduleId()
    assert zone_5.sp == 73
    assert zone_5.spC == 22.5
    assert zone_5.getSystemMode() == "cool"
    assert zone_5.tempOperation == "off"
    assert zone_5.temperature == 79 == zone_5.getTemperature()
    assert zone_5.temperatureC == 26 == zone_5.getTemperatureC()
    assert zone_5.temperatureStatus == LENNOX_STATUS_GOOD
    assert zone_5.system.sysId == "0000000-0000-0000-0000-000000000002"

    # The system now goes into cooling mode
    data = loadfile("mut_sys1_zone1_cooling_on.json")
    api.processMessage(data)
    assert zone_5_callback_all.called == 2
    assert zone_5_callback_system_mode.called == 1
    assert zone_5_callback_tempoperation.called == 1

    assert zone_5.tempOperation == "cooling"
    assert zone_5.demand == 37.5
    # Make sure nothing else changed.
    assert zone_5.name == "Zone 1"
    assert zone_5.id == 0
    assert zone_5.coolingOption is True
    assert zone_5.csp == 78 == zone_5.getCoolSP()
    assert zone_5.dehumidificationOption is True
    assert zone_5.desp == 50
    assert zone_5.emergencyHeatingOption is False
    assert zone_5.fanMode == "auto" == zone_5.getFanMode()
    assert zone_5.heatingOption is True
    assert zone_5.hsp == 68 == zone_5.getHeatSP()
    assert zone_5.humOperation == "off"
    assert zone_5.humidificationOption is False
    assert zone_5.humidity == 30 == zone_5.getHumidity()
    assert zone_5.humidityStatus == LENNOX_STATUS_GOOD

    assert zone_5.humidityMode == "off"
    assert zone_5.husp == 40 == zone_5.getHumidifySetpoint()
    assert zone_5.maxCsp == 99
    assert zone_5.maxDehumSp == 60
    assert zone_5.maxHsp == 90
    assert zone_5.minHumSp == 15
    assert zone_5.maxHumSp == 45
    assert zone_5.minCsp == 60
    assert zone_5.minHsp == 40
    assert zone_5.scheduleId == 16 == zone_5.getManualModeScheduleId()
    assert zone_5.sp == 73
    assert zone_5.getSystemMode() == "cool"
    assert zone_5.temperature == 79 == zone_5.getTemperature()
    assert zone_5.temperatureC == 26 == zone_5.getTemperatureC()
    assert zone_5.temperatureStatus == LENNOX_STATUS_GOOD
    assert zone_5.system.sysId == "0000000-0000-0000-0000-000000000002"


def test_hvac_mode_change_zone_2(api: s30api_async):
    """Tests mode change to zone 2"""
    zone_2: lennox_zone = api.system_list[0].zone_list[1]

    zone_2_callback_all = CallbackHandler()
    zone_2.registerOnUpdateCallback(zone_2_callback_all.update_callback)
    zone_2_callback_system_mode = CallbackHandler()
    zone_2.registerOnUpdateCallback(
        zone_2_callback_system_mode.update_callback, match=["systemMode"]
    )
    zone_2_callback_tempoperation_csp = CallbackHandler()
    zone_2.registerOnUpdateCallback(
        zone_2_callback_tempoperation_csp.update_callback,
        match=["tempOperation", "csp"],
    )

    data = loadfile("mut_sys0_zone2_csp.json")
    api.processMessage(data)

    assert zone_2_callback_all.called == 1
    assert zone_2_callback_system_mode.called == 0
    assert zone_2_callback_tempoperation_csp.called == 1

    assert zone_2.csp == 77 == zone_2.getCoolSP()
    # check that nothing else changed
    assert zone_2.name == "Zone 2"
    assert zone_2.id == 1
    assert zone_2.coolingOption is True
    #    assert zone_2.csp == 78 == zone_2.getCoolSP()
    assert zone_2.dehumidificationOption is True
    assert zone_2.desp == 50
    assert zone_2.emergencyHeatingOption is False
    assert zone_2.fanMode == "auto" == zone_2.getFanMode()
    assert zone_2.heatingOption is True
    assert zone_2.hsp == 69
    assert zone_2.humOperation == "off"
    assert zone_2.humidificationOption is False
    assert zone_2.humidity == 28 == zone_2.getHumidity()
    assert zone_2.humidityStatus == LENNOX_STATUS_GOOD

    assert zone_2.humidityMode == "dehumidify"
    assert zone_2.husp == 40 == zone_2.getHumidifySetpoint()
    assert zone_2.maxCsp == 99
    assert zone_2.maxDehumSp == 60
    assert zone_2.maxHsp == 90
    assert zone_2.minHumSp == 15
    assert zone_2.maxHumSp == 45
    assert zone_2.minCsp == 60
    assert zone_2.minHsp == 40
    assert zone_2.scheduleId == 17 == zone_2.getManualModeScheduleId()
    assert zone_2.sp == 73
    assert zone_2.systemMode == "cool" == zone_2.getSystemMode()
    assert zone_2.tempOperation == "off"
    assert zone_2.temperature == 78 == zone_2.getTemperature()
    assert zone_2.temperatureStatus == LENNOX_STATUS_GOOD
    assert zone_2.system.sysId == "0000000-0000-0000-0000-000000000001"


# Sometimes an config update message arrives before the full config, this
# test case checks this behavior, it does not happen often.
def test_data_before_config() -> s30api_async:
    """Test messages arriving in unexpected order"""
    api = s30api_async("myemail@email.com", "mypassword", None)

    data = loadfile("login_response.json")
    api.process_login_response(data)

    data = loadfile("config_response_system_01.json")
    api.processMessage(data)

    # Config mutation arrives before the full status.
    data = loadfile("mut_zone_config_no_status.json")
    api.processMessage(data)

    zone_5: lennox_zone = api.getSystem("0000000-0000-0000-0000-000000000002").getZone(0)
    assert zone_5 is not None
    assert zone_5.getSystemMode() is None
    assert zone_5.name is None
    assert zone_5.id == 0
    assert zone_5.coolingOption is None
    assert zone_5.csp is None
    assert zone_5.dehumidificationOption is True
    assert zone_5.desp is None
    assert zone_5.emergencyHeatingOption is None
    assert zone_5.fanMode is None
    assert zone_5.fanMode == zone_5.getFanMode()
    assert zone_5.heatingOption is None
    assert zone_5.hsp is None
    assert zone_5.hsp == zone_5.getHeatSP()
    assert zone_5.humOperation is None
    assert zone_5.humidificationOption is False
    assert zone_5.humidity is None
    assert zone_5.humidity == zone_5.getHumidity()
    assert zone_5.humidityStatus is None

    assert zone_5.humidityMode is None
    assert zone_5.husp is None
    assert zone_5.husp == zone_5.getHumidifySetpoint()
    assert zone_5.maxCsp is None
    assert zone_5.maxDehumSp is None
    assert zone_5.maxHsp is None
    assert zone_5.minHumSp is None
    assert zone_5.maxHumSp is None
    assert zone_5.minCsp is None
    assert zone_5.minHsp is None
    assert zone_5.scheduleId is None
    assert zone_5.sp is None
    assert zone_5.tempOperation is None
    assert zone_5.temperature is None
    assert zone_5.temperature == zone_5.getTemperature()
    assert zone_5.temperatureC is None
    assert zone_5.temperatureC == zone_5.getTemperatureC()
    assert zone_5.temperatureStatus is None
    assert zone_5.system.sysId == "0000000-0000-0000-0000-000000000002"

    data = loadfile("config_response_system_02.json")
    api.processMessage(data)

    assert zone_5.name == "Zone 1"
    assert zone_5.id == 0
    assert zone_5.coolingOption is True
    assert zone_5.csp == 78 == zone_5.getCoolSP()
    assert zone_5.dehumidificationOption is True
    assert zone_5.desp == 50
    assert zone_5.emergencyHeatingOption is False
    assert zone_5.fanMode == "auto" == zone_5.getFanMode()
    assert zone_5.heatingOption is True
    assert zone_5.hsp == 68 == zone_5.getHeatSP()
    assert zone_5.humOperation == "off"
    assert zone_5.humidificationOption is False
    assert zone_5.humidity == 30 == zone_5.getHumidity()
    assert zone_5.humidityStatus == LENNOX_STATUS_GOOD

    assert zone_5.humidityMode == "off"
    assert zone_5.husp == 40 == zone_5.getHumidifySetpoint()
    assert zone_5.maxCsp == 99
    assert zone_5.maxDehumSp == 60
    assert zone_5.maxHsp == 90
    assert zone_5.minHumSp == 15
    assert zone_5.maxHumSp == 45
    assert zone_5.minCsp == 60
    assert zone_5.minHsp == 40
    assert zone_5.scheduleId == 16 == zone_5.getManualModeScheduleId()
    assert zone_5.sp == 73
    assert zone_5.systemMode == "off" == zone_5.getSystemMode()
    assert zone_5.tempOperation == "off"
    assert zone_5.temperature == 79 == zone_5.getTemperature()
    assert zone_5.temperatureStatus == LENNOX_STATUS_GOOD
    assert zone_5.system.sysId == "0000000-0000-0000-0000-000000000002"


def test_ventilation_zone_status(api: s30api_async):
    """Tests processing ventilation status"""
    data = loadfile("ventilation_zone_status_on.json")
    api.processMessage(data)

    zone_5 = api.getSystem("0000000-0000-0000-0000-000000000001").getZone(0)
    assert zone_5.ventilation is True

    data = loadfile("ventilation_zone_status_off.json")
    api.processMessage(data)
    assert zone_5.ventilation is False


def test_ventilation_system_time_remaining(api: s30api_async):
    """Tests processing ventilation time remaining"""
    system = api.getSystem("0000000-0000-0000-0000-000000000001")

    system_callback_all = CallbackHandler()
    system.registerOnUpdateCallback(system_callback_all.update_callback)
    system_callback_remainingtime_and_others = CallbackHandler()
    system.registerOnUpdateCallback(
        system_callback_remainingtime_and_others.update_callback,
        ["this", "that", "ventilationRemainingTime"],
    )
    system_callback_should_not_fire = CallbackHandler()
    system.registerOnUpdateCallback(
        system_callback_should_not_fire.update_callback, ["this", "that", "other"]
    )

    data = loadfile("ventilation_system_remaining_time.json")
    api.processMessage(data)
    assert system_callback_all.called == 1
    assert system_callback_remainingtime_and_others.called == 1
    assert system_callback_should_not_fire.called == 0
    assert system.ventilationRemainingTime == 600
    assert system.ventilatingUntilTime == "1626278426"


def test_ventilation_system_on_and_off(api: s30api_async):
    """Tests ventilation turning on and off"""
    system = api.getSystem("0000000-0000-0000-0000-000000000001")

    system_callback_all = CallbackHandler()
    system.registerOnUpdateCallback(system_callback_all.update_callback)
    system_callback_ventilation_mode_and_others = CallbackHandler()
    system.registerOnUpdateCallback(
        system_callback_ventilation_mode_and_others.update_callback,
        ["this", "that", "ventilationRemainingTime", "ventilationMode"],
    )
    system_callback_should_not_fire = CallbackHandler()
    system.registerOnUpdateCallback(
        system_callback_should_not_fire.update_callback, ["this", "that", "other"]
    )

    data = loadfile("ventilation_system_off.json")
    api.processMessage(data)

    assert system_callback_all.called == 1
    assert system_callback_ventilation_mode_and_others.called == 1
    assert system_callback_should_not_fire.called == 0
    assert system.ventilationMode == "off"

    data = loadfile("ventilation_system_on.json")
    api.processMessage(data)
    assert system_callback_all.called == 2
    assert system_callback_ventilation_mode_and_others.called == 2
    assert system_callback_should_not_fire.called == 0
    assert system.ventilationMode == "on"

    data = loadfile("ventilation_system_off.json")
    api.processMessage(data)
    assert system_callback_all.called == 3
    assert system_callback_ventilation_mode_and_others.called == 3
    assert system_callback_should_not_fire.called == 0
    assert system.ventilationMode == "off"


def test_manual_away_mode_on_and_off(api: s30api_async):
    """Test away mode turning on and off"""
    system = api.getSystem("0000000-0000-0000-0000-000000000001")

    data = loadfile("manual_away_mode_on.json")
    api.processMessage(data)
    assert system.manualAwayMode is True

    data = loadfile("manual_away_mode_off.json")
    api.processMessage(data)
    assert system.manualAwayMode is False


def test_smart_away_mutations(api: s30api_async):
    """Test smart away updates"""
    system = api.getSystem("0000000-0000-0000-0000-000000000001")
    assert system.sa_enabled is True
    assert system.sa_reset is False
    assert system.sa_cancel is False
    assert system.sa_state == LENNOX_SA_STATE_ENABLED_CANCELLED
    assert system.sa_setpointState == LENNOX_SA_SETPOINT_STATE_HOME

    data = loadfile("sa_config_cancel.json")
    api.processMessage(data)
    assert system.sa_enabled is True
    assert system.sa_reset is False
    assert system.sa_cancel is True
    assert system.sa_state == LENNOX_SA_STATE_ENABLED_CANCELLED
    assert system.sa_setpointState == LENNOX_SA_SETPOINT_STATE_HOME

    system.sa_state = "Unkownn"
    system.sa_setpointState = "Unknown"
    data = loadfile("sa_status_update.json")
    api.processMessage(data)
    assert system.sa_enabled is True
    assert system.sa_reset is False
    assert system.sa_cancel is False
    assert system.sa_state == LENNOX_SA_STATE_ENABLED_CANCELLED
    assert system.sa_setpointState == LENNOX_SA_SETPOINT_STATE_HOME


def test_humidity_setpoint_mutations(api: s30api_async):
    """Test humidity setpoint updates"""
    zone_5 = api.getSystem("0000000-0000-0000-0000-000000000001").getZone(0)
    assert zone_5.getHumidityMode() == LENNOX_HUMIDITY_MODE_DEHUMIDIFY
    assert zone_5.getHumidifySetpoint() == 40
    data = loadfile("humidity_setpoint_35.json")
    api.processMessage(data)
    assert zone_5.getHumidityMode() == LENNOX_HUMIDITY_MODE_HUMIDIFY
    assert zone_5.getHumidifySetpoint() == 35
    assert zone_5.humOperation == LENNOX_HUMID_OPERATION_HUMID


def test_humidity_status(api: s30api_async):
    """Test processing humidity status"""
    zone_1 = api.getSystem("0000000-0000-0000-0000-000000000002").getZone(0)
    assert zone_1.humidityStatus == LENNOX_STATUS_GOOD

    data = loadfile("mut_sys1_zone_1_humidity_status_not_available.json")
    api.processMessage(data)
    assert zone_1.humidityStatus == LENNOX_STATUS_NOT_AVAILABLE

    data = loadfile("mut_sys1_zone_1_humidity_status_not_exist.json")
    api.processMessage(data)
    assert zone_1.humidityStatus == LENNOX_STATUS_NOT_EXIST


def test_temperature_status(api: s30api_async):
    """Test processing temperature status"""
    zone_1 = api.getSystem("0000000-0000-0000-0000-000000000002").getZone(0)
    assert zone_1.temperatureStatus == LENNOX_STATUS_GOOD

    data = loadfile("mut_sys1_zone_1_temperature_status_not_available.json")
    api.processMessage(data)
    assert zone_1.temperatureStatus == LENNOX_STATUS_NOT_AVAILABLE

    data = loadfile("mut_sys1_zone_1_temperature_status_not_exist.json")
    api.processMessage(data)
    assert zone_1.temperatureStatus == LENNOX_STATUS_NOT_EXIST


def test_outdoor_temperature_status(api: s30api_async):
    """Test outdoor temperature status"""
    lsystem = api.getSystem("0000000-0000-0000-0000-000000000002")
    assert lsystem.outdoorTemperatureStatus == LENNOX_STATUS_GOOD

    data = loadfile("mut_sys1_zone_1_outdoorTemperature_status_not_available.json")
    api.processMessage(data)
    assert lsystem.outdoorTemperatureStatus == LENNOX_STATUS_NOT_AVAILABLE

    data = loadfile("mut_sys1_zone_1_outdoorTemperature_status_not_exist.json")
    api.processMessage(data)
    assert lsystem.outdoorTemperatureStatus == LENNOX_STATUS_NOT_EXIST
