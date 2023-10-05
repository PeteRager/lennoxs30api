"""Tests for weather devices"""
# pylint: disable=line-too-long
from lennoxs30api.s30api_async import lennox_system

from tests.conftest import loadfile


def test_weather_config(api_system_04_furn_ac_zoning):
    """Tests weather config loading"""
    api = api_system_04_furn_ac_zoning
    system: lennox_system = api.system_list[0]
    assert system.sysId == "LCC"

    message = loadfile("weather.json", "LCC")
    system.processMessage(message)

    assert system.wt_is_valid is True
    assert system.wt_env_airQuality == "good"
    assert system.wt_env_tree == "extreme"
    assert system.wt_env_weed == "very high"
    assert system.wt_env_grass == "high"
    assert system.wt_env_mold == "moderate"
    assert system.wt_env_uvIndex == "low"
    assert system.wt_env_humidity == 84
    assert system.wt_env_windSpeed == 1.0
    assert system.wt_env_windSpeedK == 2.0
    assert system.wt_env_cloudCoverage == 97
    assert system.wt_env_dewpoint == 64.0
    assert system.wt_env_dewpointC == 18.0


class CallbackHandler(object):
    """Handler for callbacks"""

    def __init__(self):
        self.called = 0

    def update_callback(self):
        """Callback for changes"""
        self.called = self.called + 1


def test_weather_subscriptions(api_system_04_furn_ac_zoning):
    """Tests subscriptions"""
    api = api_system_04_furn_ac_zoning
    system: lennox_system = api.system_list[0]
    assert system.sysId == "LCC"

    message = loadfile("weather.json", "LCC")
    system.processMessage(message)

    message["Data"]["weather"]["status"]["env"]["airQuality"] = "error"
    callback_handler = CallbackHandler()
    system.registerOnUpdateCallback(callback_handler.update_callback, ["wt_env_airQuality"])

    # Test 1 - processing message should invoke callback
    system.processMessage(message)
    assert callback_handler.called == 1

    # Test 2 - reprocessing message should not invoke callback
    callback_handler.called = 0
    system.processMessage(message)
    assert callback_handler.called == 0
