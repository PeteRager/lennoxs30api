from lennoxs30api.s30api_async import lennox_zone, s30api_async, lennox_system
from lennoxs30api.lennox_home import lennox_home

import json
import os
import logging

logFormatter = logging.Formatter(
    "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
)
rootLogger = logging.getLogger()
rootLogger.setLevel(level=logging.DEBUG)

LOG_PATH = os.path.dirname(__file__)
fileHandler = logging.FileHandler("{0}/{1}.log".format(LOG_PATH, "log.txt"))
fileHandler.setFormatter(logFormatter)
fileHandler.setLevel(logging.DEBUG)
rootLogger.addHandler(fileHandler)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
consoleHandler.setLevel(logging.DEBUG)
rootLogger.addHandler(consoleHandler)


def loadfile(name) -> json:
    script_dir = os.path.dirname(__file__) + "/messages/"
    file_path = os.path.join(script_dir, name)
    with open(file_path) as f:
        data = json.load(f)
    return data


def setup_load_configuration() -> s30api_async:
    api = s30api_async("myemail@email.com", "mypassword", None)

    data = loadfile("login_response.json")
    api.process_login_response(data)

    data = loadfile("config_response_system_01.json")
    api.processMessage(data)

    data = loadfile("config_response_system_02.json")
    api.processMessage(data)
    return api


def test_hvac_mode_change_zone_5():
    api = setup_load_configuration()

    data = loadfile("mut_sys1_zone1_cool_sched.json")

    zone_5 = api.getSystem("0000000-0000-0000-0000-000000000002").getZone(0)
    assert zone_5.getSystemMode() == "off"
    api.processMessage(data)
    assert zone_5.getSystemMode() == "cool"
    # Make sure nothing else changed.
    assert zone_5.name == "Zone 1"
    assert zone_5.id == 0
    assert zone_5.coolingOption == True
    assert zone_5.csp == 78 == zone_5.getCoolSP()
    assert zone_5.dehumidificationOption == True
    assert zone_5.desp == 50
    assert zone_5.emergencyHeatingOption == False
    assert zone_5.fanMode == "auto" == zone_5.getFanMode()
    assert zone_5.heatingOption == True
    assert zone_5.hsp == 68 == zone_5.getHeatSP()
    assert zone_5.humOperation == "off"
    assert zone_5.humidificationOption == False
    assert zone_5.humidity == 30 == zone_5.getHumidity()
    assert zone_5.humidityMode == "off"
    assert zone_5.husp == 40
    assert zone_5.maxCsp == 99
    assert zone_5.maxDehumSp == 60
    assert zone_5.maxHsp == 90
    assert zone_5.maxHumSp == 45
    assert zone_5.minCsp == 60
    assert zone_5.minHsp == 40
    assert zone_5.scheduleId == 16 == zone_5.getManualModeScheduleId()
    assert zone_5.sp == 73
    assert zone_5.tempOperation == "off"
    assert zone_5.temperature == 79 == zone_5.getTemperature()
    assert zone_5.temperatureC == 26 == zone_5.getTemperatureC()
    assert zone_5._system.sysId == "0000000-0000-0000-0000-000000000002"

    # This file does not change anything.  SOmetime this message is not received.
    data = loadfile("mut_sys1_zone1_status.json")
    api.processMessage(data)

    # Make sure nothing else changed.
    assert zone_5.name == "Zone 1"
    assert zone_5.id == 0
    assert zone_5.coolingOption == True
    assert zone_5.csp == 78 == zone_5.getCoolSP()
    assert zone_5.dehumidificationOption == True
    assert zone_5.desp == 50
    assert zone_5.emergencyHeatingOption == False
    assert zone_5.fanMode == "auto" == zone_5.getFanMode()
    assert zone_5.heatingOption == True
    assert zone_5.hsp == 68 == zone_5.getHeatSP()
    assert zone_5.humOperation == "off"
    assert zone_5.humidificationOption == False
    assert zone_5.humidity == 30 == zone_5.getHumidity()
    assert zone_5.humidityMode == "off"
    assert zone_5.husp == 40
    assert zone_5.maxCsp == 99
    assert zone_5.maxDehumSp == 60
    assert zone_5.maxHsp == 90
    assert zone_5.maxHumSp == 45
    assert zone_5.minCsp == 60
    assert zone_5.minHsp == 40
    assert zone_5.scheduleId == 16 == zone_5.getManualModeScheduleId()
    assert zone_5.sp == 73
    assert zone_5.getSystemMode() == "cool"
    assert zone_5.tempOperation == "off"
    assert zone_5.temperature == 79 == zone_5.getTemperature()
    assert zone_5.temperatureC == 26 == zone_5.getTemperatureC()
    assert zone_5._system.sysId == "0000000-0000-0000-0000-000000000002"

    # The system now goes into cooling mode
    data = loadfile("mut_sys1_zone1_cooling_on.json")
    api.processMessage(data)
    assert zone_5.tempOperation == "cooling"
    # Make sure nothing else changed.
    assert zone_5.name == "Zone 1"
    assert zone_5.id == 0
    assert zone_5.coolingOption == True
    assert zone_5.csp == 78 == zone_5.getCoolSP()
    assert zone_5.dehumidificationOption == True
    assert zone_5.desp == 50
    assert zone_5.emergencyHeatingOption == False
    assert zone_5.fanMode == "auto" == zone_5.getFanMode()
    assert zone_5.heatingOption == True
    assert zone_5.hsp == 68 == zone_5.getHeatSP()
    assert zone_5.humOperation == "off"
    assert zone_5.humidificationOption == False
    assert zone_5.humidity == 30 == zone_5.getHumidity()
    assert zone_5.humidityMode == "off"
    assert zone_5.husp == 40
    assert zone_5.maxCsp == 99
    assert zone_5.maxDehumSp == 60
    assert zone_5.maxHsp == 90
    assert zone_5.maxHumSp == 45
    assert zone_5.minCsp == 60
    assert zone_5.minHsp == 40
    assert zone_5.scheduleId == 16 == zone_5.getManualModeScheduleId()
    assert zone_5.sp == 73
    assert zone_5.getSystemMode() == "cool"
    #   assert zone_5.tempOperation == 'off'
    assert zone_5.temperature == 79 == zone_5.getTemperature()
    assert zone_5.temperatureC == 26 == zone_5.getTemperatureC()
    assert zone_5._system.sysId == "0000000-0000-0000-0000-000000000002"


def test_hvac_mode_change_zone_2():
    api = setup_load_configuration()

    data = loadfile("mut_sys0_zone2_csp.json")
    api.processMessage(data)

    zone_2: lennox_zone = api.getSystems()[0].getZoneList()[1]
    assert zone_2.csp == 77 == zone_2.getCoolSP()
    # check that nothing else changed
    assert zone_2.name == "Zone 2"
    assert zone_2.id == 1
    assert zone_2.coolingOption == True
    #    assert zone_2.csp == 78 == zone_2.getCoolSP()
    assert zone_2.dehumidificationOption == True
    assert zone_2.desp == 50
    assert zone_2.emergencyHeatingOption == False
    assert zone_2.fanMode == "auto" == zone_2.getFanMode()
    assert zone_2.heatingOption == True
    assert zone_2.hsp == 69
    assert zone_2.humOperation == "off"
    assert zone_2.humidificationOption == False
    assert zone_2.humidity == 28 == zone_2.getHumidity()
    assert zone_2.humidityMode == "dehumidify"
    assert zone_2.husp == 40
    assert zone_2.maxCsp == 99
    assert zone_2.maxDehumSp == 60
    assert zone_2.maxHsp == 90
    assert zone_2.maxHumSp == 45
    assert zone_2.minCsp == 60
    assert zone_2.minHsp == 40
    assert zone_2.scheduleId == 17 == zone_2.getManualModeScheduleId()
    assert zone_2.sp == 73
    assert zone_2.systemMode == "cool" == zone_2.getSystemMode()
    assert zone_2.tempOperation == "off"
    assert zone_2.temperature == 78 == zone_2.getTemperature()
    assert zone_2._system.sysId == "0000000-0000-0000-0000-000000000001"


# Sometimes an config update message arrives before the full config, this
# test case checks this behavior, it does not happen often.
def test_data_before_config() -> s30api_async:
    api = s30api_async("myemail@email.com", "mypassword", None)

    data = loadfile("login_response.json")
    api.process_login_response(data)

    data = loadfile("config_response_system_01.json")
    api.processMessage(data)

    # Config mutation arrives before the full status.
    data = loadfile("mut_zone_config_no_status.json")
    api.processMessage(data)

    zone_5 = api.getSystem("0000000-0000-0000-0000-000000000002").getZone(0)
    assert zone_5 != None
    assert zone_5.getSystemMode() == None
    assert zone_5.name == None
    assert zone_5.id == 0
    assert zone_5.coolingOption == None
    assert zone_5.csp == None
    assert zone_5.dehumidificationOption == True
    assert zone_5.desp == None
    assert zone_5.emergencyHeatingOption == None
    assert zone_5.fanMode == None == zone_5.getFanMode()
    assert zone_5.heatingOption == None
    assert zone_5.hsp == None == zone_5.getHeatSP()
    assert zone_5.humOperation == None
    assert zone_5.humidificationOption == False
    assert zone_5.humidity == None == zone_5.getHumidity()
    assert zone_5.humidityMode == None
    assert zone_5.husp == None
    assert zone_5.maxCsp == None
    assert zone_5.maxDehumSp == None
    assert zone_5.maxHsp == None
    assert zone_5.maxHumSp == None
    assert zone_5.minCsp == None
    assert zone_5.minHsp == None
    assert zone_5.scheduleId == None
    assert zone_5.sp == None
    assert zone_5.tempOperation == None
    assert zone_5.temperature == None == zone_5.getTemperature()
    assert zone_5.temperatureC == None == zone_5.getTemperatureC()
    assert zone_5._system.sysId == "0000000-0000-0000-0000-000000000002"

    data = loadfile("config_response_system_02.json")
    api.processMessage(data)

    assert zone_5.name == "Zone 1"
    assert zone_5.id == 0
    assert zone_5.coolingOption == True
    assert zone_5.csp == 78 == zone_5.getCoolSP()
    assert zone_5.dehumidificationOption == True
    assert zone_5.desp == 50
    assert zone_5.emergencyHeatingOption == False
    assert zone_5.fanMode == "auto" == zone_5.getFanMode()
    assert zone_5.heatingOption == True
    assert zone_5.hsp == 68 == zone_5.getHeatSP()
    assert zone_5.humOperation == "off"
    assert zone_5.humidificationOption == False
    assert zone_5.humidity == 30 == zone_5.getHumidity()
    assert zone_5.humidityMode == "off"
    assert zone_5.husp == 40
    assert zone_5.maxCsp == 99
    assert zone_5.maxDehumSp == 60
    assert zone_5.maxHsp == 90
    assert zone_5.maxHumSp == 45
    assert zone_5.minCsp == 60
    assert zone_5.minHsp == 40
    assert zone_5.scheduleId == 16 == zone_5.getManualModeScheduleId()
    assert zone_5.sp == 73
    assert zone_5.systemMode == "off" == zone_5.getSystemMode()
    assert zone_5.tempOperation == "off"
    assert zone_5.temperature == 79 == zone_5.getTemperature()
    assert zone_5._system.sysId == "0000000-0000-0000-0000-000000000002"


def test_ventilation_zone_status():
    api = setup_load_configuration()

    data = loadfile("ventilation_zone_status_on.json")
    api.processMessage(data)

    zone_5 = api.getSystem("0000000-0000-0000-0000-000000000001").getZone(0)
    assert zone_5.ventilation == True

    data = loadfile("ventilation_zone_status_off.json")
    api.processMessage(data)
    assert zone_5.ventilation == False


def test_ventilation_system_time_remaining():
    api = setup_load_configuration()

    data = loadfile("ventilation_system_remaining_time.json")
    api.processMessage(data)

    system = api.getSystem("0000000-0000-0000-0000-000000000001")
    assert system.ventilationRemainingTime == 600
    assert system.ventilatingUntilTime == "1626278426"


def test_ventilation_system_on_and_off():
    api = setup_load_configuration()

    data = loadfile("ventilation_system_off.json")
    api.processMessage(data)

    system = api.getSystem("0000000-0000-0000-0000-000000000001")
    assert system.ventilationMode == "off"

    data = loadfile("ventilation_system_on.json")
    api.processMessage(data)
    assert system.ventilationMode == "on"

    data = loadfile("ventilation_system_off.json")
    api.processMessage(data)

    system = api.getSystem("0000000-0000-0000-0000-000000000001")
    assert system.ventilationMode == "off"


def test_manual_away_mode_on_and_off():
    api = setup_load_configuration()
    system = api.getSystem("0000000-0000-0000-0000-000000000001")

    data = loadfile("manual_away_mode_on.json")
    api.processMessage(data)
    assert system.manualAwayMode == True

    data = loadfile("manual_away_mode_off.json")
    api.processMessage(data)
    assert system.manualAwayMode == False
