"""Tests for WIFI interface status"""
# pylint: disable=line-too-long
import logging
from lennoxs30api.s30api_async import lennox_system

from tests.conftest import loadfile

def test_wifi_interface_config(api_system_04_furn_ac_zoning):
    """Tests wifi interface loading"""
    api = api_system_04_furn_ac_zoning
    system: lennox_system = api.system_list[0]
    assert system.sysId == "LCC"

    message = loadfile("wifi_interface_status.json", "LCC")
    system.processMessage(message)

    assert system.wifi_macAddr == "60:a4:4c:6b:d2:4c"
    assert system.wifi_ssid == "wifi_home"
    assert system.wifi_ip == "10.0.0.10"
    assert system.wifi_router == "10.0.0.1"
    assert system.wifi_dns == "8.8.8.8"
    assert system.wifi_dns2 == "4.4.4.4"
    assert system.wifi_subnetMask == "255.255.0.0"
    assert system.wifi_bitRate == 72200000
    assert system.wifi_rssi == -68

    # Test no content in message
    message["Data"]["interfaces"][0]["Info"] = {}
    system.processMessage(message)
    message["Data"]["interfaces"] = {}
    system.processMessage(message)

def test_wifi_associated(api_system_04_furn_ac_zoning, caplog):
    """Make sure the API can process this associated messages as it occurs alot.
       There is no data in the message that is needed."""
    api = api_system_04_furn_ac_zoning
    system: lennox_system = api.system_list[0]
    assert system.sysId == "LCC"

    message = loadfile("wifi_interface_associated.json", "LCC")
    with caplog.at_level(logging.WARNING):
        caplog.clear()
        system.processMessage(message)
        assert len(caplog.messages) == 0
