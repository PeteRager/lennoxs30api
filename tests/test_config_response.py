"""Tests the config response"""

from lennoxs30api.s30api_async import (
    LENNOX_ALERT_MINOR,
    LENNOX_ALERT_NONE,
    LENNOX_DEHUMIDIFICATION_MODE_AUTO,
    LENNOX_HUMIDIFICATION_MODE_BASIC,
    LENNOX_HVAC_COOL,
    LENNOX_HVAC_EMERGENCY_HEAT,
    LENNOX_HVAC_HEAT,
    LENNOX_HVAC_HEAT_COOL,
    LENNOX_HVAC_OFF,
    LENNOX_NONE_STR,
    LENNOX_SA_SETPOINT_STATE_HOME,
    LENNOX_SA_SETPOINT_STATE_AWAY,
    LENNOX_SA_SETPOINT_STATE_TRANSITION,
    LENNOX_SA_STATE_DISABLED,
    LENNOX_SA_STATE_ENABLED_CANCELLED,
    LENNOX_STATUS_GOOD,
    LENNOX_ZONING_MODE_CENTRAL,
    LENNOX_ZONING_MODE_ZONED,
    lennox_zone,
    s30api_async,
    lennox_system,
)

def test_process_configuration_message(api: s30api_async):
    """Test processing of configuration data"""
    lsystem: lennox_system = api.system_list[0]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000001"
    assert lsystem.productType == "S30"
    assert lsystem.is_s30
    assert not lsystem.is_s40
    assert lsystem.name == "Moetown North"
    assert lsystem.numberOfZones == 4
    assert lsystem.outdoorTemperature == 80
    assert lsystem.outdoorTemperatureC == 27
    assert lsystem.outdoorTemperatureStatus == LENNOX_STATUS_GOOD
    assert lsystem.temperatureUnit == "F"

    assert lsystem.indoorUnitType == "furnace"
    assert lsystem.has_indoor_unit is True
    lsystem.indoorUnitType = None
    assert lsystem.has_indoor_unit is False
    lsystem.indoorUnitType = LENNOX_NONE_STR
    assert lsystem.has_indoor_unit is False
    lsystem.indoorUnitType = "furnace"

    assert lsystem.outdoorUnitType == "air conditioner"
    assert lsystem.has_emergency_heat() is False
    assert lsystem.has_outdoor_unit is True
    lsystem.outdoorUnitType = None
    assert lsystem.has_outdoor_unit is False
    lsystem.outdoorUnitType = LENNOX_NONE_STR
    assert lsystem.has_outdoor_unit is False
    lsystem.outdoorUnitType = "air conditioner"

    assert lsystem.diagPoweredHours == 40950
    assert lsystem.diagRuntime == 15605
    assert lsystem.diagVentilationRuntime == 0
    assert lsystem.humidifierType == "none"
    assert lsystem.ventilationUnitType == "ventilator"
    assert lsystem.supports_ventilation() is True
    assert lsystem.ventilationControlMode == "timed"
    assert lsystem.feelsLikeMode is False
    assert lsystem.ventilatingUntilTime == ""

    # Away Mode and Smart Away Tests
    assert lsystem.manualAwayMode is False
    assert lsystem.manualAwayMode == lsystem.get_manual_away_mode()
    assert lsystem.sa_enabled is True
    assert lsystem.sa_reset is False
    assert lsystem.sa_cancel is False
    assert lsystem.sa_state == LENNOX_SA_STATE_ENABLED_CANCELLED
    assert lsystem.sa_setpointState == LENNOX_SA_SETPOINT_STATE_HOME
    assert lsystem.get_smart_away_mode() is False
    assert lsystem.get_away_mode() is False

    assert lsystem.centralMode is False
    assert lsystem.zoningMode == LENNOX_ZONING_MODE_ZONED
    assert lsystem.dehumidificationMode == LENNOX_DEHUMIDIFICATION_MODE_AUTO
    assert lsystem.humidificationMode == LENNOX_HUMIDIFICATION_MODE_BASIC
    assert lsystem.circulateTime == 25
    assert lsystem.enhancedDehumidificationOvercoolingC == 1
    assert lsystem.enhancedDehumidificationOvercoolingF == 2
    assert lsystem.enhancedDehumidificationOvercoolingC_inc == 0.5
    assert lsystem.enhancedDehumidificationOvercoolingC_max == 2
    assert lsystem.enhancedDehumidificationOvercoolingC_min == 0
    assert lsystem.enhancedDehumidificationOvercoolingF_inc == 1
    assert lsystem.enhancedDehumidificationOvercoolingF_max == 4
    assert lsystem.enhancedDehumidificationOvercoolingF_min == 0
    assert lsystem.enhancedDehumidificationOvercoolingF_enable is True
    assert lsystem.enhancedDehumidificationOvercoolingC_enable is True
    assert lsystem.alert == LENNOX_ALERT_MINOR

    zones = lsystem.zone_list
    assert len(zones) == 4

    zone_1: lennox_zone = zones[0]

    assert zone_1.name == "Zone 1"
    assert zone_1.id == 0
    assert zone_1.coolingOption is True
    assert zone_1.csp == 77 == zone_1.getCoolSP()
    assert zone_1.dehumidificationOption is True
    assert zone_1.desp == 50
    assert zone_1.emergencyHeatingOption is False
    assert zone_1.fanMode == "auto" == zone_1.getFanMode()
    assert zone_1.heatingOption is True
    assert zone_1.hsp == 64 == zone_1.getHeatSP()
    assert zone_1.hspC == 18
    assert zone_1.humOperation == "off"
    assert zone_1.humidificationOption is True
    assert zone_1.humidity == 28 == zone_1.getHumidity()
    assert zone_1.humidityStatus == LENNOX_STATUS_GOOD
    assert zone_1.humidityMode == "dehumidify"
    assert zone_1.husp == 40 == zone_1.getHumidifySetpoint()
    assert zone_1.maxCsp == 99
    assert zone_1.maxCspC == 37
    assert zone_1.minCsp == 60
    assert zone_1.minCspC == 15.5
    assert zone_1.maxHsp == 90
    assert zone_1.maxHspC == 32
    assert zone_1.minHsp == 40
    assert zone_1.minHspC == 4.5
    assert zone_1.sp == 73
    assert zone_1.spC == 22.5

    assert zone_1.maxDehumSp == 60
    assert zone_1.scheduleId == 16 == zone_1.getManualModeScheduleId()
    assert zone_1.systemMode == LENNOX_HVAC_HEAT == zone_1.getSystemMode()
    assert zone_1.tempOperation == "off"
    assert zone_1.temperature == 79 == zone_1.getTemperature()
    assert zone_1.temperatureC == 26 == zone_1.getTemperatureC()
    assert zone_1.temperatureStatus == LENNOX_STATUS_GOOD
    assert zone_1.heatCoast is False
    assert zone_1.defrost is False
    assert zone_1.balancePoint == "none"
    assert zone_1.aux is False
    assert zone_1.coolCoast is False
    assert zone_1.ssr is False

    assert zone_1.system.sysId == "0000000-0000-0000-0000-000000000001"

    zone_1.systemMode = LENNOX_HVAC_HEAT
    assert zone_1.getTargetTemperatureF() == zone_1.hsp
    assert zone_1.getTargetTemperatureC() == zone_1.hspC
    lsystem.single_setpoint_mode = True
    assert zone_1.getTargetTemperatureF() == zone_1.sp
    assert zone_1.getTargetTemperatureC() == zone_1.spC
    lsystem.single_setpoint_mode = False

    zone_1.systemMode = LENNOX_HVAC_EMERGENCY_HEAT
    assert zone_1.getTargetTemperatureF() == zone_1.hsp
    assert zone_1.getTargetTemperatureC() == zone_1.hspC
    lsystem.single_setpoint_mode = True
    assert zone_1.getTargetTemperatureF() == zone_1.sp
    assert zone_1.getTargetTemperatureC() == zone_1.spC
    lsystem.single_setpoint_mode = False


    zone_1.systemMode = LENNOX_HVAC_COOL
    assert zone_1.getTargetTemperatureF() == zone_1.csp
    assert zone_1.getTargetTemperatureC() == zone_1.cspC
    lsystem.single_setpoint_mode = True
    assert zone_1.getTargetTemperatureF() == zone_1.sp
    assert zone_1.getTargetTemperatureC() == zone_1.spC
    lsystem.single_setpoint_mode = False

    zone_1.systemMode = LENNOX_HVAC_OFF
    assert zone_1.getTargetTemperatureF() is None
    assert zone_1.getTargetTemperatureC() is None
    lsystem.single_setpoint_mode = True
    assert zone_1.getTargetTemperatureF() is None
    assert zone_1.getTargetTemperatureC() is None
    lsystem.single_setpoint_mode = False

    zone_1.systemMode = LENNOX_HVAC_HEAT_COOL
    assert zone_1.getTargetTemperatureF() is None
    assert zone_1.getTargetTemperatureC() is None
    lsystem.single_setpoint_mode = True
    assert zone_1.getTargetTemperatureF() == zone_1.sp
    assert zone_1.getTargetTemperatureC() == zone_1.spC
    lsystem.single_setpoint_mode = False

    zone_1.systemMode = LENNOX_HVAC_HEAT

    zone_2: lennox_zone = zones[1]

    assert zone_2.name == "Zone 2"
    assert zone_2.id == 1
    assert zone_2.coolingOption is True
    assert zone_2.csp == 78 == zone_2.getCoolSP()
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
    assert zone_2.spC == 23
    assert zone_2.systemMode == "cool" == zone_2.getSystemMode()
    assert zone_2.tempOperation == "off"
    assert zone_2.temperature == 78 == zone_2.getTemperature()
    assert zone_2.temperatureC == 25.5 == zone_2.getTemperatureC()
    assert zone_2.temperatureStatus == LENNOX_STATUS_GOOD
    assert zone_2.system.sysId == "0000000-0000-0000-0000-000000000001"

    zone_3: lennox_zone = zones[2]

    assert zone_3.name == "Zone 3"
    assert zone_3.id == 2
    assert zone_3.coolingOption is True
    assert zone_3.csp == 71 == zone_3.getCoolSP()
    assert zone_3.dehumidificationOption is True
    assert zone_3.desp == 50
    assert zone_3.emergencyHeatingOption is False
    assert zone_3.fanMode == "auto" == zone_3.getFanMode()
    assert zone_3.heatingOption is True
    assert zone_3.hsp == 40 == zone_3.getHeatSP()
    assert zone_3.humOperation == "off"
    assert zone_3.humidificationOption is False
    assert zone_3.humidity == 28 == zone_3.getHumidity()
    assert zone_3.humidityStatus == LENNOX_STATUS_GOOD
    assert zone_3.humidityMode == "dehumidify"
    assert zone_3.husp == 40 == zone_3.getHumidifySetpoint()
    assert zone_3.maxCsp == 99
    assert zone_3.maxDehumSp == 60
    assert zone_3.maxHsp == 90
    assert zone_3.minHumSp == 15
    assert zone_3.maxHumSp == 45
    assert zone_3.minCsp == 60
    assert zone_3.minHsp == 40
    assert zone_3.scheduleId == 18 == zone_3.getManualModeScheduleId()
    assert zone_3.sp == 73
    assert zone_3.spC == 23
    assert zone_3.systemMode == "cool" == zone_3.getSystemMode()
    assert zone_3.tempOperation == "cooling"
    assert zone_3.temperature == 71 == zone_3.getTemperature()
    assert zone_3.temperatureStatus == LENNOX_STATUS_GOOD
    assert zone_3.system.sysId == "0000000-0000-0000-0000-000000000001"

    zone_4: lennox_zone = zones[3]
    assert zone_4.name == "Zone 4"
    assert zone_4.id == 3
    assert zone_4.coolingOption is True
    assert zone_4.csp == 72 == zone_4.getCoolSP()
    assert zone_4.dehumidificationOption is True
    assert zone_4.desp == 50
    assert zone_4.emergencyHeatingOption is False
    assert zone_4.fanMode == "auto" == zone_4.getFanMode()
    assert zone_4.heatingOption is True
    assert zone_4.hsp == 64 == zone_4.getHeatSP()
    assert zone_4.humOperation == "off"
    assert zone_4.humidificationOption is False
    assert zone_4.humidity == 28 == zone_4.getHumidity()
    assert zone_4.humidityMode == "dehumidify"
    assert zone_4.humidityStatus == LENNOX_STATUS_GOOD
    assert zone_4.husp == 40 == zone_4.getHumidifySetpoint()
    assert zone_4.maxCsp == 99
    assert zone_4.maxDehumSp == 60
    assert zone_4.maxHsp == 90
    assert zone_4.minHumSp == 15
    assert zone_4.maxHumSp == 45
    assert zone_4.minCsp == 60
    assert zone_4.minHsp == 40
    assert zone_4.scheduleId == 19 == zone_4.getManualModeScheduleId()
    assert zone_4.sp == 73
    assert zone_4.spC == 23
    assert zone_4.systemMode == "off" == zone_4.getSystemMode()
    assert zone_4.tempOperation == "off"
    assert zone_4.temperature == 76 == zone_4.getTemperature()
    assert zone_4.temperatureStatus == LENNOX_STATUS_GOOD

    assert zone_4.system.sysId == "0000000-0000-0000-0000-000000000001"

    lsystem: lennox_system = api.system_list[1]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000002"
    assert lsystem.productType == "S30"
    assert lsystem.name == "South Moetown"
    assert lsystem.numberOfZones == 1
    assert lsystem.outdoorTemperature == 97
    assert lsystem.outdoorTemperatureC == 36
    assert lsystem.outdoorTemperatureStatus == LENNOX_STATUS_GOOD
    assert lsystem.temperatureUnit == "F"
    assert lsystem.indoorUnitType == "furnace"
    assert lsystem.outdoorUnitType == "air conditioner"
    assert lsystem.diagPoweredHours == 41071
    assert lsystem.diagRuntime == 5884
    assert lsystem.humidifierType == "none"
    assert lsystem.ventilationUnitType == "none"
    # Away Mode and Smart Away Tests
    assert lsystem.manualAwayMode is True
    assert lsystem.manualAwayMode == lsystem.get_manual_away_mode()
    assert lsystem.sa_enabled is False
    assert lsystem.sa_reset is False
    assert lsystem.sa_cancel is False
    assert lsystem.sa_state == LENNOX_SA_STATE_DISABLED
    assert lsystem.sa_setpointState == LENNOX_SA_SETPOINT_STATE_HOME
    assert lsystem.get_smart_away_mode() is False
    assert lsystem.get_away_mode() is True
    lsystem.manualAwayMode = False
    assert lsystem.get_away_mode() is False
    lsystem.sa_setpointState = LENNOX_SA_SETPOINT_STATE_AWAY
    assert lsystem.get_smart_away_mode() is False
    lsystem.sa_enabled = True
    assert lsystem.get_smart_away_mode() is True
    assert lsystem.get_away_mode() is True
    lsystem.sa_setpointState = LENNOX_SA_SETPOINT_STATE_TRANSITION
    assert lsystem.get_smart_away_mode() is True
    assert lsystem.get_away_mode() is True

    assert lsystem.centralMode is False
    assert lsystem.zoningMode == LENNOX_ZONING_MODE_CENTRAL
    assert lsystem.dehumidificationMode == LENNOX_DEHUMIDIFICATION_MODE_AUTO
    assert lsystem.humidificationMode == LENNOX_HUMIDIFICATION_MODE_BASIC
    assert lsystem.circulateTime == 15
    assert lsystem.enhancedDehumidificationOvercoolingC == 1
    assert lsystem.enhancedDehumidificationOvercoolingF == 2
    assert lsystem.enhancedDehumidificationOvercoolingC_inc == 0.5
    assert lsystem.enhancedDehumidificationOvercoolingC_max == 2
    assert lsystem.enhancedDehumidificationOvercoolingC_min == 0
    assert lsystem.enhancedDehumidificationOvercoolingF_inc == 1
    assert lsystem.enhancedDehumidificationOvercoolingF_max == 4
    assert lsystem.enhancedDehumidificationOvercoolingF_min == 0
    assert lsystem.alert == LENNOX_ALERT_NONE

    assert lsystem.alerts_num_cleared is None
    assert lsystem.alerts_num_active is None
    assert lsystem.alerts_last_cleared_id is None
    assert lsystem.alerts_num_in_active_array is None
    assert len(lsystem.active_alerts) == 0

    zone_5: lennox_zone = lsystem.zone_list[0]
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
    assert zone_5.spC == 22.5
    assert zone_5.systemMode == "off" == zone_5.getSystemMode()
    assert zone_5.tempOperation == "off"
    assert zone_5.temperature == 79 == zone_5.getTemperature()
    assert zone_5.temperatureStatus == LENNOX_STATUS_GOOD
    assert zone_5.system.sysId == "0000000-0000-0000-0000-000000000002"


def test_process_configuration_heatpump(api: s30api_async):
    """Tests the heatpump configuration"""
    lsystem: lennox_system = api.system_list[2]
    assert lsystem.sysId == "0000000-0000-0000-0000-000000000003"
    assert lsystem.productType == "S30"
    assert lsystem.name == "West Moetown"
    assert lsystem.numberOfZones == 1
    assert lsystem.indoorUnitType == "furnace"
    assert lsystem.outdoorUnitType == "heat pump"
    assert lsystem.has_emergency_heat() is True
